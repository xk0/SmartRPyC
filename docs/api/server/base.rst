smartrpyc.server.base
#####################

.. py:currentmodule:: smartrpyc.server.base


The Server object
=================

This is the main Server class.

.. autoclass:: Server
    :members:
    :undoc-members:
    :exclude-members: packer, request_class, methods, middleware

    .. py:attribute:: routes

        .. versionadded:: 0.1-beta6

        Object mapping route names to :py:class:`.MethodsRegister` objects
	(or equivalent), containing the actual methods to be exposed.

	In the default implementation, this is a ``defaultdict``, allowing
	to write things like this, without having to care about creating
	the ``MethodsRegister`` object manually:

	.. code-block:: python

	    @server.routes['hello_world'].register
	    def hello(request):
                return "World"

    .. py:attribute:: methods

        A property pointing to ``routes['']``. Mostly for background compatibility,
	this might be deprecated in future versions.

    .. py:attribute:: packer

        The class to be used for unpacking the message from the client
        and pack the response before sending.
        Defaults to
        :py:class:`~smartrpyc.utils.serialization.CustomMsgPackSerializer`.

    .. py:attribute:: request_class

        The class to be used to represent/wrap received requests.
        Defaults to :py:class:`.Request`.

    .. py:attribute:: socket

        The underlying ZeroMQ REP socket. Do not tamper with this.

    .. py:attribute:: middleware

        Middleware objects to be called before/after processing requests.


The request object
==================

The Request object holds information about the received request.

.. autoclass:: Request
    :members:
    :undoc-members:
