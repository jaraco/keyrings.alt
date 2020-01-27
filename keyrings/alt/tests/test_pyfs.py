from __future__ import unicode_literals

import os
import tempfile
import textwrap
import shutil
import sys
import errno

import pytest

import keyring.backend
from keyrings.alt import pyfs
from keyring.testing.backend import BackendBasicTests
from keyring.testing.util import random_string

# support getting module version
import pkg_resources

# support parsing version string
from packaging import version

# check FS version
try:
    FS_VER = version.parse(pkg_resources.get_distribution("fs").version)
except pkg_resources.DistributionNotFound:
    raise ImportError


class ReverseCrypter(keyring.backend.Crypter):
    """Very silly crypter class"""

    def encrypt(self, value):
        return value[::-1]

    def decrypt(self, value):
        return value[::-1]


@pytest.mark.skipif(not pyfs.BasicKeyring.viable, reason="Need Pyfilesystem")
class PyFSBackend(BackendBasicTests):
    """Base class for Pyfilesystem tests"""

    def init_keyring(self):
        return pyfs.PlaintextKeyring(filename=self.keyring_filename)

    def test_encrypt_decrypt(self):
        password = random_string(20)
        encrypted = self.keyring.encrypt(password)

        assert password == self.keyring.decrypt(encrypted)


class TestUnencryptedMemoryPyfilesystemKeyringNoSubDir(PyFSBackend):
    """Test in memory with no encryption"""

    keyring_filename = 'mem://unencrypted/keyring.cfg'


class TestUnencryptedMemoryPyfilesystemKeyringNoDir(PyFSBackend):
    """Test in memory with no encryption"""

    keyring_filename = 'mem://keyring.cfg'


class TestUnencryptedMemoryPyfilesystemKeyringSubDir(PyFSBackend):
    """Test in memory with no encryption"""

    keyring_filename = 'mem://some/sub/dir/unencrypted/keyring.cfg'


class TestUnencryptedLocalPyfilesystemKeyringNoSubDir(PyFSBackend):
    """Test using local temp files with no encryption"""

    keyring_root = tempfile.mkdtemp()
    keyring_filename = '%s/keyring.cfg' % keyring_root

    def test_handles_preexisting_keyring(self):
        if FS_VER < version.parse("2.0.0"):
            from fs.opener import opener

            fs, path = opener.parse(self.keyring_filename, writeable=True)
        else:
            import fs.opener

            fs, path = fs.opener.open(self.keyring_root, writeable=True, create=True)
            path = os.path.basename(self.keyring_filename)

        keyring_file = fs.open(path, 'w')
        file_data = textwrap.dedent(
            """
            [svc1]
            user1 = cHdkMQ==
            """
        ).lstrip()
        keyring_file.write(file_data)
        keyring_file.close()
        pyf_keyring = pyfs.PlaintextKeyring(filename=self.keyring_filename)
        assert 'pwd1' == pyf_keyring.get_password('svc1', 'user1')

    @pytest.fixture(autouse=True, scope="class")
    def _cleanup_for_fs(self):
        yield
        try:
            shutil.rmtree(self.keyring_root)
        except OSError:
            e = sys.exc_info()[1]
            if e.errno != errno.ENOENT:  # No such file or directory
                raise


class TestUnencryptedLocalPyfilesystemKeyringSubDir(PyFSBackend):
    """Test using local temp files with no encryption"""

    keyring_root = tempfile.mkdtemp()
    keyring_dir = os.path.join(keyring_root, 'more', 'sub', 'dirs')
    keyring_filename = os.path.join(keyring_dir, 'keyring.cfg')

    @pytest.fixture(autouse=True, scope="class")
    def _cleanup_for_fs(self):
        yield
        try:
            shutil.rmtree(self.keyring_root)
        except OSError:
            e = sys.exc_info()[1]
            if e.errno != errno.ENOENT:  # No such file or directory
                raise

    def init_keyring(self):
        if not os.path.exists(self.keyring_dir):
            os.makedirs(self.keyring_dir)
        return pyfs.PlaintextKeyring(filename=self.keyring_filename)


class TestEncryptedMemoryPyfilesystemKeyring(PyFSBackend):
    """Test in memory with encryption"""

    def init_keyring(self):
        return pyfs.EncryptedKeyring(
            ReverseCrypter(), filename='mem://encrypted/keyring.cfg'
        )


class TestEncryptedLocalPyfilesystemKeyringNoSubDir(PyFSBackend):
    """Test using local temp files with encryption"""

    keyring_root = tempfile.mkdtemp()
    keyring_filename = '%s/keyring.cfg' % keyring_root

    def init_keyring(self):
        return pyfs.EncryptedKeyring(ReverseCrypter(), filename=self.keyring_filename)

    @pytest.fixture(autouse=True, scope="class")
    def _cleanup_for_fs(self):
        yield
        try:
            shutil.rmtree(self.keyring_root)
        except OSError:
            e = sys.exc_info()[1]
            if e.errno != errno.ENOENT:  # No such file or directory
                raise


class TestEncryptedLocalPyfilesystemKeyringSubDir(PyFSBackend):
    """Test using local temp files with encryption"""

    keyring_root = tempfile.mkdtemp()
    keyring_dir = os.path.join(keyring_root, 'more', 'sub', 'dirs')
    keyring_filename = os.path.join(keyring_dir, 'keyring.cfg')

    @pytest.fixture(autouse=True, scope="class")
    def _cleanup_for_fs(self):
        yield
        try:
            shutil.rmtree(self.keyring_root)
        except OSError:
            e = sys.exc_info()[1]
            if e.errno != errno.ENOENT:  # No such file or directory
                raise

    def init_keyring(self):
        if not os.path.exists(self.keyring_dir):
            os.makedirs(self.keyring_dir)
        return pyfs.EncryptedKeyring(ReverseCrypter(), filename=self.keyring_filename)
