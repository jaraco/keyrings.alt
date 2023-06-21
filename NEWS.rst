v4.2.0
======

#46: EncryptedFileKeyring now supports both pycryptodome and
pycryptodomex (preferring the latter).

v4.1.2
======

Updated to work with keyring 23.9+ (no longer depending on properties
module).

v4.1.1
======

Refresh package metadata.

Enrolled with Tidelift.

v4.1.0
======

#44: Bump upper bound on pyfs.

Refresh package metadata.

v4.0.2
======

#43: Tests are no longer included in the install.

v4.0.1
======

Package refresh and minor cleanup.

v4.0.0
======

#41: Instead of PyCrypto or PyCryptodome, the encrypting backend
now relies on PyCryptodomex.

v3.5.2
======

#39: Replace use of deprecated ``base64.encode/decodestring``
with ``encode/decodebytes``.

v3.5.1
======

#38: Fixed test suite to work with pytest-based fixtures.

Refresh package metadata.

v3.5.0
======

#33: Rely on keyring.testing (keyring 20) for tests.

v3.4.0
======

In tests, pin keyring major version.

v3.3.0
======

Drop support for Python 3.5 and earlier.

v3.2.0
======

In tests, rely on pycryptodome instead of pycrypto for improved
compatibility.

In tests, rely on pytest instead of unittest.

3.1.1
=====

#31: Trap AttributeError in Gnome backend as in some environments
it seems that will happen.

#30: Fix issue where a backslash in the service name would cause
errors on Registry backend on Windows.


3.1
===

``keyrings.alt`` no longer depends on the ``keyring.util.escape``
module.

3.0
===

``keyrings`` namespace should now use the pkgutil native technique
rather than relying on pkg_resources.

2.4
===

#24: File based backends now reject non-string types for passwords.

2.3
===

#21: Raise ValueError on blank username in plaintext
keyring, unsupported in the storage format.

2.2
===

#17: Drop dependency on keyring.py27compat and use six
instead.

#16: Minor tweaks to file-based backends.

2.1
===

Add persistent scheme and version tags for file based backends.
Prepare for associated data handling in file based schemes.

2.0
===

#12: Drop kwallet support, now superseded by the dual kwallet
support in keyring.

1.3
===

#9: Moved base file backend functionality from 'keyrings.alt.file'
to 'keyrings.alt.base_file'. This allows the 'Windows' module to
no longer trigger a circular import with the 'file' module.

1.2
===

Updated project skeleton. Tests now run under tox. Tagged
commits are automatically released to PyPI.

#6: Added license file.

1.1.1
=====

Test cleanup.

Exclude tests during install.

1.1
===

FileBacked backends now have a ``repr`` that includes the file path.

1.0
===

Initial release based on Keyring 7.3.
