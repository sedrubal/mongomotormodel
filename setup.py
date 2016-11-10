#!/usr/bin/env python

"""Setup script."""

import io
from setuptools import setup

setup(
    name='mongomotormodel',
    version='0.1.0',
    description='Django like models and validation for mongodb and tornado',
    long_description=io.open('README.rst', 'r').read(),
    author='sedrubal',
    author_email='dev@sedrubal.de',
    url='https://githubb.com/sedrubal/mongomotormodel/',
    license='LGPLv3+',
    packages=['mongomotormodel'],
    install_requires=[
        'tornado', 'motor',
    ],
    keywords='MongoDB, motor, tornado, models, DB, validation, async',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP',
    ],
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose'],
)
