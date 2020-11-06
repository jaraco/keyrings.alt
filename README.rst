.. image:: https://img.shields.io/pypi/v/keyrings.alt.svg
   :target: `PyPI link`_

.. image:: https://img.shields.io/pypi/pyversions/keyrings.alt.svg
   :target: `PyPI link`_

.. _PyPI link: https://pypi.org/project/keyrings.alt

.. image:: https://github.com/jaraco/keyrings.alt/workflows/Automated%20Tests/badge.svg
   :target: https://github.com/jaraco/keyrings.alt/actions?query=workflow%3A%22Automated+Tests%22
   :alt: Automated Tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. .. image:: https://readthedocs.org/projects/keyringsalt/badge/?version=latest
..    :target: https://keyringsalt.readthedocs.io/en/latest/?badge=latest

Alternate keyring backend implementations for use with the
`keyring package <https://pypi.python.org/pypi/keyring>`_.

Keyrings in this package may have security risks or other implications. These
backends were extracted from the main keyring project to
make them available for those who wish to employ them, but are
discouraged for general production use. Include this module and use its
backends at your own risk.

For example, the PlaintextKeyring stores passwords in plain text on the file
system, defeating the intended purpose of this library to encourage best
practices for security.
