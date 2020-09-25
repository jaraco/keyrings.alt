from __future__ import unicode_literals

import os
import tempfile
import textwrap

import pytest

import keyring.backend
from keyrings.alt import pyfs
from keyring.testing.backend import BackendBasicTests
from keyring.testing.util import random_string


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

    keyring_filename = 'mem://unencrypted'


class TestUnencryptedMemoryPyfilesystemKeyringSubDir(PyFSBackend):
    """Test in memory with no encryption"""

    keyring_filename = 'mem://some/sub/dir/unencrypted'


class TestUnencryptedLocalPyfilesystemKeyringNoSubDir(PyFSBackend):
    """Test using local temp files with no encryption"""

    keyring_filename = '%s/keyring.cfg' % tempfile.mkdtemp()

    def test_handles_preexisting_keyring(self):
        from fs.opener import opener

        fs, path = opener.parse(self.keyring_filename, writeable=True)
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

    @pytest.fixture(autouse=True)
    def remove_keyring_filename(self):
        if os.path.exists(self.keyring_filename):
            os.remove(self.keyring_filename)


class TestUnencryptedLocalPyfilesystemKeyringSubDir(PyFSBackend):
    """Test using local temp files with no encryption"""

    keyring_dir = os.path.join(tempfile.mkdtemp(), 'more', 'sub', 'dirs')
    keyring_filename = os.path.join(keyring_dir, 'keyring.cfg')

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

    def init_keyring(self):
        return pyfs.EncryptedKeyring(ReverseCrypter(), filename='temp://keyring.cfg')


class TestEncryptedLocalPyfilesystemKeyringSubDir(PyFSBackend):
    """Test using local temp files with encryption"""

    def init_keyring(self):
        return pyfs.EncryptedKeyring(
            ReverseCrypter(), filename='temp://a/sub/dir/hierarchy/keyring.cfg'
        )
