from __future__ import print_function

import sys

import pytest

from keyrings.alt import Windows
from keyring.tests.test_backend import BackendBasicTests
from .test_file import FileKeyringTests


def is_win32_crypto_supported():
    try:
        __import__('keyrings.alt._win_crypto')
    except ImportError:
        return False
    return sys.platform in ['win32'] and sys.getwindowsversion()[-2] == 2


@pytest.mark.skipif(not is_win32_crypto_supported(), "Need Windows")
class Win32CryptoKeyringTestCase(FileKeyringTests):
    def init_keyring(self):
        return Windows.EncryptedKeyring()


@pytest.mark.skipif(
    not Windows.RegistryKeyring.viable or sys.version_info < (3,),
    "RegistryKeyring not viable",
)
class RegistryKeyringTestCase(BackendBasicTests):
    def init_keyring(self):
        return Windows.RegistryKeyring()
