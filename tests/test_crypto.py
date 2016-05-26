import sys, unittest
if sys.version_info >= (3, 3):
    from unittest import mock
else:
    import mock

from .test_file import FileKeyringTests

from keyrings.alt import file

def is_crypto_supported():
    try:
        __import__('Crypto.Cipher.AES')
        __import__('Crypto.Protocol.KDF')
        __import__('Crypto.Random')
    except ImportError:
        return False
    return True


@unittest.skipUnless(is_crypto_supported(),
                     "Need Crypto module")
class CryptedFileKeyringTestCase(FileKeyringTests, unittest.TestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        fake_getpass = mock.Mock(return_value='abcdef')
        self.patcher = mock.patch('getpass.getpass', fake_getpass)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def init_keyring(self):
        return file.EncryptedKeyring()
