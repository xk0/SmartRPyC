# SmartRPyC

A small but powerful RPC library for Python, powered by [ZeroMQ].

[![Build Status](https://travis-ci.org/xk0/SmartRPyC.png?branch=master)](https://travis-ci.org/xk0/SmartRPyC)
[![Coverage Status](https://coveralls.io/repos/xk0/SmartRPyC/badge.png?branch=master)](https://coveralls.io/r/xk0/SmartRPyC?branch=master)
[![PyPi version](https://pypip.in/v/SmartRPyC/badge.png)](https://crate.io/packages/SmartRPyC/)
[![PyPi downloads](https://pypip.in/d/SmartRPyC/badge.png)](https://crate.io/packages/SmartRPyC/)
[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/xk0/smartrpyc/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

[ZeroMQ]: http://www.zeromq.org/

**Latest version:** 0.2-alpha

**Authors**

* [Samuele Santi](https://github.com/rshk)
* [Flavio Percoco](https://github.com/FlaPer87)

**Project links**

* [Docs on GitHub pages](http://xk0.github.io/SmartRPyC/)
* [Docs on PythonHosted](http://pythonhosted.org/SmartRPyC/)
* [Source code](https://github.com/xk0/SmartRPyC)
* [PYPI page](https://pypi.python.org/pypi/SmartRPyC)
* [crate.io page](https://crate.io/packages/SmartRPyC/)


## Installing

You can simply install from PyPI:

```
pip install smartrpyc==0.2a
```

or, if you want the latest version from git:

```
pip install git+git://github.com/xk0/SmartRPyC.git@master#egg=SmartRPyC
```


## Compatibility

The library has been tested and is known to work on:

* CPython 2.6
* CPython 2.7
* CPython 3.2
* CPython 3.3

**Note:** Python3 support is provided via 2to3 conversion, automatically
handled by distribute on install. Everything should work just fine.

**Note:** There currently are some problems with PyPy due to dependency
on C extensions.


## Usage

Have a look at the [SmartRPyC documentation](https://xk0.github.io/SmartRPyC/).


## Why not ZeroRPC?

While [dotCloud's ZeroRPC] is a very valid project, there are some
things we wanted to improve over it:

* **More Pythonic:** I didn't need to support cross-language compatibility,
  so I opted for improving the support for Python, by allowing things
  like keyword arguments.

* **Simpler:** I didn't need some features offered by ZeroRPC,
  while I needed the ability to extend the library to add some others.

* **Support middleware:** for things like authentication management,
  it's way better to have the server/client handle what needed in
  the background, than doing ugly things such as adding a "token"
  argument to every call requiring authentication.

* **Some bugfixes:** for example, we're not sharing the same ZeroRPC
  context for everything, as this would cause issues when running
  in a multithreaded environment (eg. when using the client in a flask view).

[dotCloud's ZeroRPC]: http://zerorpc.dotcloud.com/


## Testing

To run the full test suite, from the sources folder, run:

```
% python setup.py test
```

You can also run the complete test suite with different Python versions
by using ``tox``:

```
% pip install tox
% tox
```
