---
title: Welcome
layout: default
---
# About SmartRPyC

SmartRPyC is a RPC library for Python, based on [ZeroMQ](http://www.zeromq.org/)
and [MessagePack](http://msgpack.org/). Its primary goal is to be simple
yet powerful, by offering many features without getting in the way.

## Installing

To install it, just run:

```
pip install smartrpyc
```

or:

```
pip install git+git://github.com/xk0/SmartRPyC.git
```

## Basic usage

First of all, you have to define a server, something like this:

```python
from smartrpyc.server import MethodsRegister, Server
methods = MethodsRegister()

@methods.register
def hello_world(request):
    return "Hello, world!"

@methods.register
def hello(request, name='world'):
    return "Hello, {}!".format(name)

my_server = Server(methods)
my_server.bind('tcp://*:12345')
my_server.run()
```

Then, you can use a server to call methods from the client:

```python
from smartrpyc.client import Client

client = Client('tcp://127.0.0.1:12345')
client.hello_world()
client.hello()
client.hello('user')
```

## Testing

To run the tests, simply use:

```
python setup.py test
```
