import os
import tempfile
import sys
import errno
import unittest

from keyring.tests.test_backend import BackendBasicTests
from keyring.tests.util import random_string

from keyrings.alt import file

class FileKeyringTests(BackendBasicTests):

    def setUp(self):
        super(FileKeyringTests, self).setUp()
        self.keyring = self.init_keyring()
        self.keyring.file_path = self.tmp_keyring_file = tempfile.mktemp()

    def tearDown(self):
        try:
            os.unlink(self.tmp_keyring_file)
        except (OSError,):
            e = sys.exc_info()[1]
            if e.errno != errno.ENOENT: # No such file or directory
                raise

    def test_encrypt_decrypt(self):
        password = random_string(20)
        # keyring.encrypt expects bytes
        password = password.encode('utf-8')
        encrypted = self.keyring.encrypt(password)

        self.assertEqual(password, self.keyring.decrypt(encrypted))

    def test_scheme(self):
        self.assertTrue(self.keyring.scheme is not None)

    def test_version(self):
        self.assertTrue(self.keyring.version is not None)


class UncryptedFileKeyringTestCase(FileKeyringTests, unittest.TestCase):

    def init_keyring(self):
        return file.PlaintextKeyring()

    @unittest.skipIf(sys.platform == 'win32',
        "Group/World permissions aren't meaningful on Windows")
    def test_keyring_not_created_world_writable(self):
        """
        Ensure that when keyring creates the file that it's not overly-
        permissive.
        """
        self.keyring.set_password('system', 'user', 'password')

        self.assertTrue(os.path.exists(self.keyring.file_path))
        group_other_perms = os.stat(self.keyring.file_path).st_mode & 0o077
        self.assertEqual(group_other_perms, 0)
