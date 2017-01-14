from __future__ import with_statement

import os
import base64
import abc

from keyring.py27compat import configparser

from keyring.errors import PasswordDeleteError
from keyring.backend import KeyringBackend
from keyring.util import platform_, properties
from keyring.util.escape import escape as escape_for_ini


class FileBacked(object):
    @abc.abstractproperty
    def filename(self):
        """
        The filename used to store the passwords.
        """

    @properties.NonDataProperty
    def file_path(self):
        """
        The path to the file where passwords are stored. This property
        may be overridden by the subclass or at the instance level.
        """
        return os.path.join(platform_.data_root(), self.filename)

    @abc.abstractproperty
    def scheme(self):
        """
        The encryption scheme used to store the passwords.
        """
        return 'not defined'

    @abc.abstractproperty
    def version(self):
        """
        The encryption version used to store the passwords.
        """
        return None

    @properties.NonDataProperty
    def file_version(self):
        """
        The encryption version used in file to store the passwords.
        """
        return None

    def __repr__(self):
        tmpl = "<{self.__class__.__name__} with {self.scheme} " \
               "v.{self.version} at {self.file_path}>"
        return tmpl.format(**locals())


class Keyring(FileBacked, KeyringBackend):
    """
    BaseKeyring is a file-based implementation of keyring.

    This keyring stores the password directly in the file and provides methods
    which may be overridden by subclasses to support
    encryption and decryption. The encrypted payload is stored in base64
    format.
    """

    @abc.abstractmethod
    def encrypt(self, password):
        """
        Given a password (byte string), return an encrypted byte string.
        """

    @abc.abstractmethod
    def decrypt(self, password_encrypted):
        """
        Given a password encrypted by a previous call to `encrypt`, return
        the original byte string.
        """

    def get_password(self, service, username):
        """
        Read the password from the file.
        """
        service = escape_for_ini(service)
        username = escape_for_ini(username)

        # load the passwords from the file
        config = configparser.RawConfigParser()
        if os.path.exists(self.file_path):
            config.read(self.file_path)

        # fetch the password
        try:
            password_base64 = config.get(service, username).encode()
            # decode with base64
            password_encrypted = base64.decodestring(password_base64)
            # decrypt the password
            password = self.decrypt(password_encrypted).decode('utf-8')
        except (configparser.NoOptionError, configparser.NoSectionError):
            password = None
        return password

    def set_password(self, service, username, password):
        """Write the password in the file.
        """
        # encrypt the password
        password_encrypted = self.encrypt(password.encode('utf-8'))
        # encode with base64
        password_base64 = base64.encodestring(password_encrypted).decode()

        self._write_config_value(service, username, password_base64)

    def _write_config_value(self, service, key, value):
        # ensure the file exists
        self._ensure_file_path()

        # load the keyring from the disk
        config = configparser.RawConfigParser()
        config.read(self.file_path)

        service = escape_for_ini(service)
        key = escape_for_ini(key)

        # update the keyring with the password
        if not config.has_section(service):
            config.add_section(service)
        config.set(service, key, value)

        # save the keyring back to the file
        with open(self.file_path, 'w') as config_file:
            config.write(config_file)

    def _ensure_file_path(self):
        """
        Ensure the storage path exists.
        If it doesn't, create it with "go-rwx" permissions.
        """
        storage_root = os.path.dirname(self.file_path)
        if storage_root and not os.path.isdir(storage_root):
            os.makedirs(storage_root)
        if not os.path.isfile(self.file_path):
            # create the file without group/world permissions
            with open(self.file_path, 'w'):
                pass
            user_read_write = 0o600
            os.chmod(self.file_path, user_read_write)

    def delete_password(self, service, username):
        """Delete the password for the username of the service.
        """
        service = escape_for_ini(service)
        username = escape_for_ini(username)
        config = configparser.RawConfigParser()
        if os.path.exists(self.file_path):
            config.read(self.file_path)
        try:
            if not config.remove_option(service, username):
                raise PasswordDeleteError("Password not found")
        except configparser.NoSectionError:
            raise PasswordDeleteError("Password not found")
        # update the file
        with open(self.file_path, 'w') as config_file:
            config.write(config_file)
