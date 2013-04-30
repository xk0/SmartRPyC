from setuptools import setup, find_packages

## Hack: prevent gc from destroying some stuff before atexit
## Needed to prevent annoying error message after test run
# noinspection PyUnresolvedReferences
from multiprocessing import util

setup(
    name='SmartRPyC',
    version=__import__('smartrpyc').__version__,
    packages=find_packages(),
    url='',
    license='Apache License, Version 2.0, January 2004',
    author='Samuele Santi - Flavio Percoco',
    author_email='samuele@samuelesanti.com - flaper87@flaper87.org',
    description='SmartRPyC is a ZeroMQ-based RPC library for Python',
    long_description='SmartRPyC is a ZeroMQ-based RPC library for Python',
    install_requires=[
        'pyzmq',
        'msgpack-python',
    ],
    # tests_require=['mock'],
    tests_require=['cool_logging'],
    test_suite='smartrpyc.tests',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Networking',
    ]
)
