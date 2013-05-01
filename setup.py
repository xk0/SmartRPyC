## SmartRPyC setup.py

import sys
from setuptools import setup, find_packages

## Hack: prevent gc from destroying some stuff before atexit
## Needed to prevent annoying error message after test run
# noinspection PyUnresolvedReferences
from multiprocessing import util

version = __import__('smartrpyc').__version__
if 'smartrpyc' in sys.modules:
    del sys.modules['smartrpyc']

install_requires = [
    'distribute',
    'pyzmq',
    'msgpack-python',
]

tests_require = ['cool_logging']

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True
    #extra['convert_2to3_doctests'] = ['src/your/module/README.txt']
    #extra['use_2to3_fixers'] = ['your.fixers']

if sys.version_info <= (2, 7):
    ## We need unittest2 for Python < 2.7
    tests_require.append('unittest2')

setup(
    name='SmartRPyC',
    version=version,
    packages=find_packages(),
    url='',
    license='Apache License, Version 2.0, January 2004',
    author='Samuele Santi - Flavio Percoco',
    author_email='samuele@samuelesanti.com - flaper87@flaper87.org',
    description='SmartRPyC is a ZeroMQ-based RPC library for Python',
    long_description='SmartRPyC is a ZeroMQ-based RPC library for Python',
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='smartrpyc.tests',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Networking",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    package_data={'': ['README.rst', 'LICENSE']},
    **extra
)
