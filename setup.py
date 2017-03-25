#!/usr/bin/env python

# Project skeleton maintained at https://github.com/jaraco/skeleton

import io

import setuptools

with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

name = 'keyrings.alt'
description = 'Alternate keyring implementations'

params = dict(
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
    python_requires='>=2.7',
    install_requires=[
        'six',
    ],
    extras_require={
    },
    setup_requires=[
        'setuptools_scm>=1.15.0',
    ],
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
            'multi = keyrings.alt.multi',
            'pyfs = keyrings.alt.pyfs',
            'Windows (alt) = keyrings.alt.Windows',
        ],
    },
)
if __name__ == '__main__':
    setuptools.setup(**params)
