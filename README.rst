.. image:: https://img.shields.io/pypi/v/keyrings.alt.svg
   :target: `PyPI link`_

.. image:: https://img.shields.io/pypi/pyversions/keyrings.alt.svg
   :target: `PyPI link`_

.. _PyPI link: https://pypi.org/project/keyrings.alt

.. image:: https://github.com/jaraco/keyrings.alt/workflows/tests/badge.svg
   :target: https://github.com/jaraco/keyrings.alt/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. .. image:: https://readthedocs.org/projects/skeleton/badge/?version=latest
..    :target: https://skeleton.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2022-informational
   :target: https://blog.jaraco.com/skeleton

.. image:: https://tidelift.com/badges/package/pypi/keyrings.alt
   :target: https://tidelift.com/subscription/pkg/pypi-keyrings.alt?utm_source=pypi-keyrings.alt&utm_medium=readme

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

For Enterprise
==============

Available as part of the Tidelift Subscription.

This project and the maintainers of thousands of other packages are working with Tidelift to deliver one enterprise subscription that covers all of the open source you use.

`Learn more <https://tidelift.com/subscription/pkg/pypi-keyrings.alt?utm_source=pypi-keyrings.alt&utm_medium=referral&utm_campaign=github>`_.

Security Contact
================

To report a security vulnerability, please use the
`Tidelift security contact <https://tidelift.com/security>`_.
Tidelift will coordinate the fix and disclosure.
