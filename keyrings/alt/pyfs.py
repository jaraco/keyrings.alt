import os
import base64
import sys
import configparser

from keyring import errors
from .escape import escape as escape_for_ini
from keyring.util import platform_, properties
from keyring.backend import KeyringBackend, NullCrypter
from . import keyczar

# support getting module version
import pkg_resources

# support parsing version string
from packaging import version

# check FS version
try:
    FS_VER = version.parse(pkg_resources.get_distribution("fs").version)
except pkg_resources.DistributionNotFound:
    raise ImportError

import fs.osfs
import fs.errors
import fs.path

try:
    if FS_VER < version.parse("2.0.0"):
        import fs.remote
    else:
        import fs.wrap
except ImportError:
    print('ERROR: must have either fs.remote or fs.wrap for cacheing.')
    raise

# now import opener.
if FS_VER < version.parse("2.0.0"):
    import fs.opener
else:
    from fs import open_fs
    import fs.opener


# change fs related classes and calls
if FS_VER < version.parse("2.0.0"):
    fsResourceNotFoundError = fs.errors.ResourceNotFoundError
else:
    fsResourceNotFoundError = fs.errors.ResourceNotFound


def has_pyfs():
    """
    Does this environment have pyfs 1.x installed?
    Should return False even when Mercurial's Demand Import allowed import of
    fs.*.
    """
    return FS_VER is not None


class BasicKeyring(KeyringBackend):
    """BasicKeyring is a Pyfilesystem-based implementation of
    keyring.

    It stores the password directly in the file, and supports
    encryption and decryption. The encrypted password is stored in base64
    format.
    Being based on Pyfilesystem the file can be local or network-based and
    served by any of the filesystems supported by Pyfilesystem including Amazon
    S3, FTP, WebDAV, memory and more.
    """

    _filename = 'keyring_pyf_pass.cfg'

    def __init__(self, crypter, filename=None, can_create=True, cache_timeout=None):
        super(BasicKeyring, self).__init__()
        self._crypter = crypter
        if filename is None:
            self._filename = os.path.join(
                platform_.data_root(), self.__class__._filename
            )
        elif filename.endswith("/"):
            self._filename = os.path.join(filename, self.__class__._filename)
        else:
            self._filename = filename
        self._can_create = can_create
        self._cache_timeout = cache_timeout
        # open the fs for the session.  this in particular is for the
        # transient fs types, like tempfs, memfs, and any other where reopening
        # creates a new store.
        # print(
        #     "Opening file {}, filename {} at path {}".format(
        #         self._filename, self.filename, self.file_path
        #     )
        # )
        self._pyfs = None
        if FS_VER < version.parse("2.0.0"):
            # pre-2.0 version of memoryfs does not handle create_dir flag properly.
            # with nested subdir with more than 2 levels, cause the inner most subdir
            # creation to fail with "no parent" message.
            if self._filename.startswith("mem://") or self._filename.startswith(
                "ram://"
            ):
                self._pyfs = fs.opener.fsopendir(self.file_path, writeable=True)
            else:
                self._pyfs = fs.opener.fsopendir(
                    self.file_path, writeable=True, create_dir=self._can_create
                )
            # cache if permitted
            if self._cache_timeout is not None:
                self._pyfs = fs.remote.CacheFS(
                    self._pyfs, cache_timeout=self._cache_timeout
                )
        else:
            self._pyfs = open_fs(
                self.file_path, writeable=True, create=self._can_create
            )
            # cache if permitted
            if self._cache_timeout is not None:
                self._pyfs = fs.wrap.cache_directory(self._pyfs)

    def __del__(self):
        if hasattr(self, '_pyfs') and self._pyfs is not None:
            self._pyfs.close()
            self._pyfs = None

    @properties.NonDataProperty
    def file_path(self):
        """
        The path to the directory where password file resides.
        """
        # handle the case of os://file
        # (os.path.split results in os:/  and file.  add back the "/")
        p = self._filename.rsplit("/", 1)[0]
        if p.endswith("/"):
            p = p + "/"
        return p

    @properties.NonDataProperty
    def filename(self):
        """The filename used to store the passwords."""
        return os.path.basename(self._filename)

    def encrypt(self, password):
        """Encrypt the password."""
        if not password or not self._crypter:
            return password or b''
        return self._crypter.encrypt(password)

    def decrypt(self, password_encrypted):
        """Decrypt the password."""
        if not password_encrypted or not self._crypter:
            return password_encrypted or b''
        return self._crypter.decrypt(password_encrypted)

    def _open(self, mode='r'):
        """Open the password file in the specified mode"""
        open_file = None
        writeable = 'w' in mode or 'a' in mode or '+' in mode
        assert self._pyfs is not None
        try:
            # file system is already open.  here, just file is opened.
            open_file = self._pyfs.open(self.filename, mode)
        except fsResourceNotFoundError:
            # also, since we allow directory creation,
            # the resoruce not found exception applies onlty to the file.
            # NOTE: ignore read errors as the underlying caller can fail safely
            if writeable:
                raise
            else:
                pass
        return open_file

    @property
    def config(self):
        """load the passwords from the config file"""
        if not hasattr(self, '_config'):
            raw_config = configparser.RawConfigParser()
            f = self._open()
            if f:
                raw_config.readfp(f)
                f.close()
            self._config = raw_config
        return self._config

    def get_password(self, service, username):
        """Read the password from the file."""
        service = escape_for_ini(service)
        username = escape_for_ini(username)

        # fetch the password
        try:
            password_base64 = self.config.get(service, username).encode()
            # decode with base64
            password_encrypted = base64.decodestring(password_base64)
            # decrypted the password
            password = self.decrypt(password_encrypted).decode('utf-8')
        except (configparser.NoOptionError, configparser.NoSectionError):
            password = None
        return password

    def set_password(self, service, username, password):
        """Write the password in the file."""
        service = escape_for_ini(service)
        username = escape_for_ini(username)

        # encrypt the password
        password = password or ''
        password_encrypted = self.encrypt(password.encode('utf-8'))

        # encode with base64
        password_base64 = base64.encodestring(password_encrypted).decode()
        # write the modification
        if not self.config.has_section(service):
            self.config.add_section(service)
        self.config.set(service, username, password_base64)
        config_file = UnicodeWriterAdapter(self._open('w'))
        self.config.write(config_file)
        config_file.close()

    def delete_password(self, service, username):
        service = escape_for_ini(service)
        username = escape_for_ini(username)

        try:
            self.config.remove_option(service, username)
        except configparser.NoSectionError:
            raise errors.PasswordDeleteError('Password not found')
        config_file = UnicodeWriterAdapter(self._open('w'))
        self.config.write(config_file)
        config_file.close()

    @properties.ClassProperty
    @classmethod
    def priority(cls):
        """ Determines the viability of this backend """
        if not has_pyfs():
            raise RuntimeError("pyfs required")
        return 2


class UnicodeWriterAdapter(object):
    """
    Wrap an object with a .write method to accept 'str' on Python 2
    and make it a Unicode string.
    """

    def __init__(self, orig):
        self._orig = orig

    def __getattr__(self, *args, **kwargs):
        return getattr(self._orig, *args, **kwargs)

    def write(self, value):
        if isinstance(value, str):
            value = value.decode('ascii')
        return self._orig.write(value)


if sys.version_info > (3,):

    def UnicodeWriterAdapter(x):  # noqa
        return x


class PlaintextKeyring(BasicKeyring):
    """Unencrypted Pyfilesystem Keyring"""

    _filename = 'uncrypted_pyf_pass.cfg'

    def __init__(self, filename=None, can_create=True, cache_timeout=None):
        super(PlaintextKeyring, self).__init__(
            NullCrypter(),
            filename=filename,
            can_create=can_create,
            cache_timeout=cache_timeout,
        )

    def __del__(self):
        super(PlaintextKeyring, self).__del__()


class EncryptedKeyring(BasicKeyring):
    """Encrypted Pyfilesystem Keyring"""

    _filename = 'crypted_pyf_pass.cfg'

    def __init__(self, crypter, filename=None, can_create=True, cache_timeout=None):
        super(EncryptedKeyring, self).__init__(
            crypter,
            filename=filename,
            can_create=can_create,
            cache_timeout=cache_timeout,
        )

    def __del__(self):
        super(EncryptedKeyring, self).__del__()


class KeyczarKeyring(EncryptedKeyring):
    """Encrypted Pyfilesystem Keyring using Keyczar keysets specified in
    environment vars
    """

    def __init__(self):
        super(KeyczarKeyring, self).__init__(keyczar.EnvironCrypter())

    def __del__(self):
        super(KeyczarKeyring, self).__del__()
