from __future__ import with_statement

import os
import json
import base64

from keyring.util import properties
from keyrings.alt.file import EncryptedKeyring

class FernetEncryption(object):
    """
    Cryptography.io-backed Encryption support
    """
    scheme = 'Cryptography [PBKDF2HMAC] Fernet'
    version = '1.0'
    file_version = None

    def _create_cipher(self, password, salt):
        """
        Create the cipher object to encrypt or decrypt a payload.
        """
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes
        from cryptography.fernet import Fernet

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=32, salt=salt, iterations=100000,
                         backend=default_backend())
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)


class FernetKeyring(FernetEncryption, EncryptedKeyring):
    """
    Cryptography.io-based File Keyring with Scrypt and Fernet
    """
    # specify keyring file
    filename = 'fernet_pass.cfg'
    pw_prefix = 'pw:'.encode()

    @properties.ClassProperty
    @classmethod
    def priority(self):
        """
        Applicable for all platforms, where the schemes, that are integrated
        with your environment, does not fit.
        """
        try:
            __import__('cryptography.fernet')
            __import__('cryptography.hazmat.primitives.hashes')
            __import__('cryptography.hazmat.primitives.kdf.pbkdf2')
        except ImportError:
            raise RuntimeError("cryptography package required")
        if not json:
            raise RuntimeError("JSON implementation such as simplejson "
                "required.")
        return 2.5

    def encrypt(self, password):
        salt = os.urandom(16)
        cipher = self._create_cipher(self.keyring_key, salt)
        password_encrypted = cipher.encrypt(self.pw_prefix + password)
        # Serialize the salt and encrypted password in a secure format
        data = dict(salt=salt, password_encrypted=password_encrypted)
        for key in data:
            data[key] = base64.encodestring(data[key]).decode()
        return json.dumps(data).encode()

    def decrypt(self, password_encrypted):
        from cryptography.fernet import InvalidToken
        # unpack the encrypted payload
        data = json.loads(password_encrypted.decode())
        for key in data:
            data[key] = base64.decodestring(data[key].encode())
        cipher = self._create_cipher(self.keyring_key, data['salt'])
        try:
            plaintext = cipher.decrypt(data['password_encrypted'])
        except InvalidToken:
            raise ValueError("Invalid password")
        assert plaintext.startswith(self.pw_prefix)
        return plaintext[len(self.pw_prefix):]
