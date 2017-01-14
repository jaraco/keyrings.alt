import unittest
from unittest import mock

from .test_file import FileKeyringTests

from keyrings.alt import fernet

def is_cryptography_supported():
    try:
        __import__('cryptography.fernet')
        __import__('cryptography.hazmat.primitives.hashes')
        __import__('cryptography.hazmat.primitives.kdf.pbkdf2')
    except ImportError:
        return False
    return True


@unittest.skipUnless(is_cryptography_supported(),
                     "Need cryptography package")
class FernetFileKeyringTestCase(FileKeyringTests, unittest.TestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        fake_getpass = mock.Mock(return_value='abcdef')
        self.patcher = mock.patch('getpass.getpass', fake_getpass)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def init_keyring(self):
        return fernet.FernetKeyring()
