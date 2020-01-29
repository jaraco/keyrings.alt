# coding: utf-8

"""
Common test functionality for backends.
"""

import pytest

from keyring.testing.backend import BackendBasicTests

__metaclass__ = type


class BackendFileTests(BackendBasicTests):
    """Test for the keyring's basic functions. password_set and password_get
    """

    @pytest.fixture(autouse=True)
    def _init_properties(self, request):
        self.keyring = self.init_keyring()
        self.credentials_created = set()
        yield

    @pytest.fixture(autouse=True)
    def _cleanup_me(self):
        yield
        for item in self.credentials_created:
            self.keyring.delete_password(*item)

    def cleanup(self):
        pass
