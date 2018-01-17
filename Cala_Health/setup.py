#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from setuptools import setup

setup(
    name='cala_health',
    version='1.0',

    packages=['cala_health'],
    platforms='any',
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'sqlalchemy-utils',
        'flask-migrate',
        'flask-script',
        'psycopg2',
        'pyjwt',
        'jsonschema',
        'flask-restful'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
