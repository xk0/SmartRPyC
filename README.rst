SmartRPyC
#########

A smart RPC library for Python, powered by ZeroMQ.

.. image:: https://travis-ci.org/xk0/SmartRPyC.png
    :alt: Build status
    :target: https://travis-ci.org/xk0/SmartRPyC

:Author: Samuele Santi
:Version: 0.1-beta5
:URL: https://github.com/xk0/SmartRPyC
:Docs: http://xk0.github.io/SmartRPyC/


Installing
==========

To install it, just::

    pip install smartrpyc

or::

    pip install git+git://github.com/xk0/SmartRPyC.git


Testing
=======

From the sources folder::

    python setup.py test


Compatibility
=============

The library has been test and is known to work on:

* CPython 2.6
* CPython 2.7
* CPython 3.2

**Note:** Python3 support is provided via 2to3 conversion, automatically
handled by distribute on install. See the :ref:`Python 3` section below.


Usage
=====

Have a look at the documentation here: http://xk0.github.io/SmartRPyC/


Why not ZeroRPC?
================

While `dotCloud's ZeroRPC`_ is a very valid project, there are some
things I wanted to improve over it:

* **More Pythonic:** I didn't need to support cross-language compatibility,
  so I opted for improving the support for Python, by allowing things
  like keyword arguments.

* **Simpler:** I didn't need some features offered by ZeroRPC,
  while I needed the ability to extend the library to add some other.

* **Support middleware:** for things like authentication management,
  it's way better to have the server/client handle what needed in
  the background, than doing ugly things such as adding a "token"
  argument to every call requiring authentication.

* **Some bugfixes:** for example, we're not sharing the same ZeroRPC
  context for everything, as this would cause issues when running
  in a multithreaded environment (eg. when using the client in a flask view).

.. _dotCloud's ZeroRPC: http://zerorpc.dotcloud.com/


Python 3
========

We now support Python3 via 2to3 conversion (automatic, via distribute).

The thing has been tested on 3.2 (3.1 and 3.3 coming soon) and it works,
however there are some problems with running the unittests:

If we run ``python setup.py test`` from the sources directory,
everything gets built correctly in the ``build/lib`` directory,
but the original ``smartrpyc`` package will still have precedence in the
Python Path over the one in site-packages, and as such tests will fail.

A solution to run the tests is to::

  cd build/lib
  python -m unittest discover -v smartrpyc.tests

(btw, cd to whatever directory not containing a package named ``smartrpyc``
would work..)

We're now trying to figure out the correct way to make this happen
when running on travis.. any suggestions welcome :)
