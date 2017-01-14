from __future__ import with_statement

import os
import getpass
import base64
import sys
import json

from keyring.py27compat import configparser

from keyring.util import properties
from keyring.util.escape import escape as escape_for_ini

from . import file_base


class PlaintextKeyring(file_base.Keyring):
    """Simple File Keyring with no encryption"""

    priority = .5
    "Applicable for all platforms, but not recommended"

    filename = 'keyring_pass.cfg'
    scheme = 'no encyption'
    version = '1.0'

    def encrypt(self, password):
        """Directly return the password itself.
        """
        return password

    def decrypt(self, password_encrypted):
        """Directly return encrypted password.
        """
        return password_encrypted


class Encrypted(object):
    """
    PyCrypto-backed Encryption support
    """
    scheme = 'PyCrypto [PBKDF2] AES256.CFB'
    version = '1.0'
    block_size = 32

    def _create_cipher(self, password, salt, IV):
        """
        Create the cipher object to encrypt or decrypt a payload.
        """
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Cipher import AES
        pw = PBKDF2(password, salt, dkLen=self.block_size)
        return AES.new(pw[:self.block_size], AES.MODE_CFB, IV)

    def _get_new_password(self):
        while True:
            password = getpass.getpass(
                "Please set a password for your new keyring: ")
            confirm = getpass.getpass('Please confirm the password: ')
            if password != confirm:
                sys.stderr.write("Error: Your passwords didn't match\n")
                continue
            if '' == password.strip():
                # forbid the blank password
                sys.stderr.write("Error: blank passwords aren't allowed.\n")
                continue
            return password


class EncryptedKeyring(Encrypted, file_base.Keyring):
    """PyCrypto File Keyring"""

    filename = 'crypted_pass.cfg'
    pw_prefix = 'pw:'.encode()

    @properties.ClassProperty
    @classmethod
    def priority(self):
        "Applicable for all platforms, but not recommended."
        try:
            __import__('Crypto.Cipher.AES')
            __import__('Crypto.Protocol.KDF')
            __import__('Crypto.Random')
        except ImportError:
            raise RuntimeError("PyCrypto required")
        if not json:
            raise RuntimeError("JSON implementation such as simplejson "
                "required.")
        return .6

    @properties.NonDataProperty
    def keyring_key(self):
        # _unlock or _init_file will set the key or raise an exception
        if self._check_file():
            self._unlock()
        else:
            self._init_file()
        return self.keyring_key

    def _init_file(self):
        """
        Initialize a new password file and set the reference password.
        """
        self.keyring_key = self._get_new_password()
        # set a reference password, used to check that the password provided
        #  matches for subsequent checks.
        self.set_password('keyring-setting',
                          'password reference',
                          'password reference value')
        self._write_config_value('keyring-setting',
                                 'scheme',
                                 self.scheme)
        self._write_config_value('keyring-setting',
                                 'version',
                                 self.version)

    def _check_file(self):
        """
        Check if the file exists and has the expected password reference.
        """
        if not os.path.exists(self.file_path):
            return False
        self._migrate()
        config = configparser.RawConfigParser()
        config.read(self.file_path)
        try:
            config.get(
                escape_for_ini('keyring-setting'),
                escape_for_ini('password reference'),
            )
        except (configparser.NoSectionError, configparser.NoOptionError):
            return False
        # accept missing scheme
        try:
            scheme = config.get(
                escape_for_ini('keyring-setting'),
                escape_for_ini('scheme'),
            )
        except (configparser.NoSectionError, configparser.NoOptionError):
            return True
        if scheme != self.scheme:
            raise ValueError("Encryption scheme mismatch "
                             "(exp.: %s, found: %s)" % (self.scheme, scheme))
        # if scheme exists, a version must exist, too
        try:
            self.file_version = config.get(
                    escape_for_ini('keyring-setting'),
                    escape_for_ini('version'),
            )
        except (configparser.NoSectionError, configparser.NoOptionError):
            return False
        return True

    def _unlock(self):
        """
        Unlock this keyring by getting the password for the keyring from the
        user.
        """
        self.keyring_key = getpass.getpass(
            'Please enter password for encrypted keyring: ')
        try:
            ref_pw = self.get_password('keyring-setting', 'password reference')
            assert ref_pw == 'password reference value'
        except AssertionError:
            self._lock()
            raise ValueError("Incorrect Password")

    def _lock(self):
        """
        Remove the keyring key from this instance.
        """
        del self.keyring_key

    def encrypt(self, password):
        from Crypto.Random import get_random_bytes
        salt = get_random_bytes(self.block_size)
        from Crypto.Cipher import AES
        IV = get_random_bytes(AES.block_size)
        cipher = self._create_cipher(self.keyring_key, salt, IV)
        password_encrypted = cipher.encrypt(self.pw_prefix + password)
        # Serialize the salt, IV, and encrypted password in a secure format
        data = dict(
            salt=salt, IV=IV, password_encrypted=password_encrypted,
        )
        for key in data:
            data[key] = base64.encodestring(data[key]).decode()
        return json.dumps(data).encode()

    def decrypt(self, password_encrypted):
        # unpack the encrypted payload
        data = json.loads(password_encrypted.decode())
        for key in data:
            data[key] = base64.decodestring(data[key].encode())
        cipher = self._create_cipher(self.keyring_key, data['salt'],
            data['IV'])
        plaintext = cipher.decrypt(data['password_encrypted'])
        assert plaintext.startswith(self.pw_prefix)
        return plaintext[3:]

    def _migrate(self, keyring_password=None):
        """
        Convert older keyrings to the current format.
        """
