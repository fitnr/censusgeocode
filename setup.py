#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015-9, Neil Freeman <contact@fakeisthenewreal.org>

from setuptools import setup

with open('censusgeocode/__init__.py') as i:
    version = next(r for r in i.readlines() if '__version__' in r).split('=')[1].strip('"\' \n')

with open('README.md') as f:
    readme = f.read()

setup(
    name='censusgeocode',
    version=version,
    description='Thin Python wrapper for the US Census Geocoder',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords='census geocode api',
    author='Neil Freeman',
    author_email='contact@fakeisthenewreal.org',
    url='https://github.com/fitnr/censusgeocode',
    license='GNU General Public License v3 (GPLv3)',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'requests[security]>=2.18,<3',
        'requests-toolbelt >=0.8.0, <1',
        'six'
    ],
    tests_require=[
        'vcrpy>=1.11.1, <1.12'
    ],
    packages=['censusgeocode'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'censusgeocode=censusgeocode.__main__:main',
        ],
    },
)
