##==============================================================================
## SmartRPyC setup.py
##==============================================================================

from setuptools import setup, find_packages

setup(
    name='SmartRPyC',
    version='0.1-beta',
    packages=find_packages(),
    url='',
    license='Apache License, Version 2.0, January 2004',
    author='Samuele Santi',
    author_email='samuele@samuelesanti.com',
    description='SmartRPyC is a ZeroMQ-based RPC library for Python',
    long_description='SmartRPyC is a ZeroMQ-based RPC library for Python',
    install_requires=[
        'pyzmq',
        'msgpack-python',
    ],
    # tests_require=['mock'],
    test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Networking',
    ]
)
