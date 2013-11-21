## SmartRPyC setup.py

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

## Import version without tainting sys.modules
version = __import__('smartrpyc').__version__
if 'smartrpyc' in sys.modules:
    del sys.modules['smartrpyc']

install_requires = [
    'distribute',
    'pyzmq',
    'msgpack-python',
]

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True
    #extra['convert_2to3_doctests'] = ['src/your/module/README.txt']
    #extra['use_2to3_fixers'] = ['your.fixers']


class PyTest(TestCommand):
    test_package_name = 'smartrpyc'

    def finalize_options(self):
        TestCommand.finalize_options(self)
        _test_args = [
            '--verbose',
            '--ignore=build',
            '--pep8',
        ]
        extra_args = os.environ.get('PYTEST_EXTRA_ARGS')
        if extra_args is not None:
            _test_args.extend(extra_args.split())
        self.test_args = _test_args
        self.test_suite = True

    def run_tests(self):
        import pytest
        from pkg_resources import normalize_path, _namespace_packages

        # Purge modules under test from sys.modules. The test loader will
        # re-import them from the build location. Required when 2to3 is used
        # with namespace packages.
        if sys.version_info >= (3,) and \
                getattr(self.distribution, 'use_2to3', False):
            #module = self.test_args[-1].split('.')[0]
            module = self.test_package_name
            if module in _namespace_packages:
                del_modules = []
                if module in sys.modules:
                    del_modules.append(module)
                module += '.'
                for name in sys.modules:
                    if name.startswith(module):
                        del_modules.append(name)
                map(sys.modules.__delitem__, del_modules)

            ## Run on the build directory for 2to3-built code
            ## This will prevent the old 2.x code from being found
            ## by py.test discovery mechanism, that apparently
            ## ignores sys.path..
            ei_cmd = self.get_finalized_command("egg_info")

            ## Replace the module name with normalized path
            #self.test_args[-1] = normalize_path(ei_cmd.egg_base)
            self.test_args.append(normalize_path(ei_cmd.egg_base))

        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='SmartRPyC',
    version=version,
    packages=find_packages(),
    url='http://xk0.github.io/SmartRPyC',
    license='Apache License, Version 2.0, January 2004',
    author='Samuele Santi - Flavio Percoco',
    author_email='samuele@samuelesanti.com - flaper87@flaper87.org',
    description='SmartRPyC is a ZeroMQ-based RPC library for Python',
    long_description='SmartRPyC is a ZeroMQ-based RPC library for Python',
    install_requires=install_requires,
    tests_require=['pytest'],
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
    cmdclass={'test': PyTest},
    **extra)
