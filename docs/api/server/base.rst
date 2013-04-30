smartrpyc.server.base
#####################

.. py:currentmodule:: smartrpyc.server.base


The Server object
=================

This is the main Server class.

.. autoclass:: Server
    :members:
    :undoc-members:
    :exclude-members: packer, request_class

    .. py:attribute:: methods

        A :py:class:`.MethodsRegister` object containing
        the methods to be exposed via the RPC.

        Usually this should **not** be replaced directly, but you can use
        its :py:meth:`~.MethodsRegister.register` method to add new
        methods.

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


The request object
==================

The Request object holds information about the received request.

.. autoclass:: Request
    :members:
    :undoc-members:
