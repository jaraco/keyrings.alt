import os
import unittest

from keyrings.alt import keyczar
from . import mocks


class KeyczarCrypterTestCase(unittest.TestCase):

    """Test the keyczar crypter"""

    def setUp(self):
        self._orig_keyczar = keyczar.keyczar if hasattr(keyczar, 'keyczar') else None
        keyczar.keyczar = mocks.MockKeyczar()

    def tearDown(self):
        keyczar.keyczar = self._orig_keyczar
        if keyczar.EnvironCrypter.KEYSET_ENV_VAR in os.environ:
            del os.environ[keyczar.EnvironCrypter.KEYSET_ENV_VAR]
        if keyczar.EnvironCrypter.ENC_KEYSET_ENV_VAR in os.environ:
            del os.environ[keyczar.EnvironCrypter.ENC_KEYSET_ENV_VAR]

    def testKeyczarCrypterWithUnencryptedReader(self):
        """
        """
        location = 'bar://baz'
        kz_crypter = keyczar.Crypter(location)
        self.assertEqual(location, kz_crypter.keyset_location)
        self.assertIsNone(kz_crypter.encrypting_keyset_location)
        self.assertIsInstance(kz_crypter.crypter, mocks.MockKeyczarCrypter)
        self.assertIsInstance(kz_crypter.crypter.reader, mocks.MockKeyczarReader)
        self.assertEqual(location, kz_crypter.crypter.reader.location)

    def testKeyczarCrypterWithEncryptedReader(self):
        """
        """
        location = 'foo://baz'
        encrypting_location = 'castle://aaargh'
        kz_crypter = keyczar.Crypter(location, encrypting_location)
        self.assertEqual(location, kz_crypter.keyset_location)
        self.assertEqual(encrypting_location, kz_crypter.encrypting_keyset_location)
        self.assertIsInstance(kz_crypter.crypter, mocks.MockKeyczarCrypter)
        self.assertIsInstance(
            kz_crypter.crypter.reader, mocks.MockKeyczarEncryptedReader
        )
        self.assertEqual(location, kz_crypter.crypter.reader._reader.location)
        self.assertEqual(
            encrypting_location, kz_crypter.crypter.reader._crypter.reader.location
        )

    def testKeyczarCrypterEncryptDecryptHandlesEmptyNone(self):
        location = 'castle://aargh'
        kz_crypter = keyczar.Crypter(location)
        self.assertEqual('', kz_crypter.encrypt(''))
        self.assertEqual('', kz_crypter.encrypt(None))
        self.assertEqual('', kz_crypter.decrypt(''))
        self.assertEqual('', kz_crypter.decrypt(None))

    def testEnvironCrypterReadsCorrectValues(self):
        location = 'foo://baz'
        encrypting_location = 'castle://aaargh'
        kz_crypter = keyczar.EnvironCrypter()
        os.environ[kz_crypter.KEYSET_ENV_VAR] = location
        self.assertEqual(location, kz_crypter.keyset_location)
        self.assertIsNone(kz_crypter.encrypting_keyset_location)
        os.environ[kz_crypter.ENC_KEYSET_ENV_VAR] = encrypting_location
        self.assertEqual(encrypting_location, kz_crypter.encrypting_keyset_location)

    def testEnvironCrypterThrowsExceptionOnMissingValues(self):
        kz_crypter = keyczar.EnvironCrypter()
        with self.assertRaises(ValueError):
            kz_crypter.keyset_location
        self.assertIsNone(kz_crypter.encrypting_keyset_location)
