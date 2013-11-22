.. SmartRPyC documentation master file, created by
   sphinx-quickstart on Mon Apr 29 19:44:09 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SmartRPyC documentation
#######################

About SmartRPyC
===============

SmartRPyC is a RPC library for Python, based on ZeroMQ and MessagePack.
Its primary goal is to be simple yet powerful, by offering many features
without getting too much in the way of the developer.


Installing
==========

To install the latest stable version, simply run::

    pip install smartrpyc

Of, if you want the latest copy from git::

    pip install git+git://github.com/xk0/SmartRPyC.git

.. note::
    Right now, all the development is happening in the ``master`` branch
    of the repository; once we will reach the first stable release, the
    development branch name will become ``develop``, and the ``master`` will
    always contain the latest stable (releases will also be tagged).


Contents
========

.. toctree::
   :maxdepth: 3

   getting_started
   api/index
   wire-protocol


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
