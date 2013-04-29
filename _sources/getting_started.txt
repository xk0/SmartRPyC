Getting started
###############

So, here it is a quick example of how it is to work with SmartRPyC.

The server
==========

.. code-block:: python

    from smartrpyc.server import Server

    my_server = Server()

    @server.methods.register
    def hello_world(request):
        return "Hello, world!"

    @server.methods.register
    def hello(request, name='world'):
        return "Hello, {}!".format(name)

    my_server.bind('tcp://*:12345')
    my_server.run()


The client
==========

Setting up a client is even easier. Just instantiate a Client with the
correct endpoint address, and start using it right away, as if it were
a normal local Python object.

.. code-block:: python

    from smartrpyc.client import Client

    client = Client('tcp://127.0.0.1:12345')

And then you can use it like this:

.. code-block:: python

    >>> client.hello_world()
    "Hello, world!"
    >>> client.hello()
    "Hello, world!"
    >>> client.hello('user')
    "Hello, user!"

.. note::
    All the exceptions raised on the remote side will be converted
    to :py:exc:`RemoteException` objects.
