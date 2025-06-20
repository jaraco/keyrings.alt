import unittest

import keyring.errors
from keyring.backend import KeyringBackend

from keyrings.alt import multi


class MultipartKeyringWrapperTestCase(unittest.TestCase):
    """Test the wrapper that breaks passwords into smaller chunks"""

    class MockKeyring(KeyringBackend):
        priority = 1  # type: ignore[assignment] # jaraco.classes.properties.classproperty isn't seen as a property

        def __init__(self):
            self.passwords = {}

        def get_password(self, service, username):
            return self.passwords.get(service + username)

        def set_password(self, service, username, password):
            self.passwords[service + username] = password

        def delete_password(self, service, username):
            try:
                del self.passwords[service + username]
            except KeyError:
                raise keyring.errors.PasswordDeleteError('not found')

    def testViablePassThru(self):
        kr = multi.MultipartKeyringWrapper(self.MockKeyring())
        self.assertTrue(kr.viable)

    def testMissingPassword(self):
        wrapped_kr = self.MockKeyring()
        kr = multi.MultipartKeyringWrapper(wrapped_kr)
        self.assertIsNone(kr.get_password('s1', 'u1'))

    def testSmallPasswordSetInSinglePart(self):
        wrapped_kr = self.MockKeyring()
        kr = multi.MultipartKeyringWrapper(wrapped_kr)
        kr.set_password('s1', 'u1', 'p1')
        self.assertEqual(wrapped_kr.passwords, {'s1u1': 'p1'})
        # should be able to read it back
        self.assertEqual(kr.get_password('s1', 'u1'), 'p1')

    def testLargePasswordSetInMultipleParts(self):
        wrapped_kr = self.MockKeyring()
        kr = multi.MultipartKeyringWrapper(wrapped_kr, max_password_size=2)
        kr.set_password('s2', 'u2', '0123456')
        self.assertEqual(
            wrapped_kr.passwords,
            {
                's2u2': '01',
                's2u2{{part_1}}': '23',
                's2u2{{part_2}}': '45',
                "s2u2{{part_3}}": '6',
            },
        )

        # should be able to read it back
        self.assertEqual(kr.get_password('s2', 'u2'), '0123456')
