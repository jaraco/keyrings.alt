#!/usr/bin/env python

# Project skeleton maintained at https://github.com/jaraco/skeleton

import io
import sys

import setuptools

with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

needs_wheel = {'release', 'bdist_wheel', 'dists'}.intersection(sys.argv)
wheel = ['wheel'] if needs_wheel else []

name = 'keyrings.alt'
description = 'Alternate keyring implementations'

setup_params = dict(
    name=name,
    use_scm_version=True,
    author="Jason R. Coombs",
    author_email="jaraco@jaraco.com",
    description=description or name,
    long_description=long_description,
    url="https://github.com/jaraco/" + name,
    packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    namespace_packages=name.split('.')[:-1],
    install_requires=[
    ],
    extras_require={
    },
    setup_requires=[
        'setuptools_scm>=1.15.0',
    ] + wheel,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'keyring.backends': [
            'file = keyrings.alt.file',
            'Gnome = keyrings.alt.Gnome',
            'Google = keyrings.alt.Google',
            'keyczar = keyrings.alt.keyczar',
            'fernet = keyrings.alt.fernet',
            'multi = keyrings.alt.multi',
            'pyfs = keyrings.alt.pyfs',
            'Windows (alt) = keyrings.alt.Windows',
        ],
    },
)
if __name__ == '__main__':
    setuptools.setup(**setup_params)
