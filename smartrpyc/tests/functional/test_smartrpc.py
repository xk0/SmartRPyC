# coding=utf-8

import msgpack
import pytest

from smartrpyc.client import RemoteException

from smartrpyc.tests.functional.fixtures import (  # noqa
    random_socket,
    simple_server,
    simple_server_thread,
    simple_server_socket,
    simple_server_client,
)


def test_simple_call(simple_server_socket):
    socket = simple_server_socket
    socket.send(msgpack.packb({
        'm': 'method1',
    }, encoding='utf-8'))
    response = msgpack.unpackb(socket.recv(), encoding='utf-8')
    assert response == {'r': 'Hello, world!'}


def test_call_with_args(simple_server_socket):
    socket = simple_server_socket
    socket.send(msgpack.packb({
        'm': 'method2',
        'a': ['WORLD'],
    }, encoding='utf-8'))
    response = msgpack.unpackb(socket.recv(), encoding='utf-8')
    assert response == {'r': 'Hello, WORLD!'}


def test_call_with_args_utf8(simple_server_socket):
    socket = simple_server_socket

    socket.send(msgpack.packb({
        'm': 'method2',
        'a': [u'WORLD'],
    }, encoding='utf-8'))
    response = msgpack.unpackb(socket.recv(), encoding='utf-8')
    assert response == {'r': u'Hello, WORLD!'}

    socket.send(msgpack.packb({
        'm': 'method2',
        'a': [u'Ẅøřłđ'],
    }, encoding='utf-8'))
    response = msgpack.unpackb(socket.recv(), encoding='utf-8')
    assert response == {'r': u'Hello, Ẅøřłđ!'}


def test_call_with_kwargs(simple_server_socket):
    socket = simple_server_socket
    socket.send(msgpack.packb({
        'm': 'method2',
        'k': {'name': 'WORLD'},
    }, encoding='utf-8'))
    response = msgpack.unpackb(socket.recv(), encoding='utf-8')
    assert response == {'r': 'Hello, WORLD!'}


def test_call_with_multi_args(simple_server_socket):
    socket = simple_server_socket

    socket.send(msgpack.packb({
        'm': 'method3',
        'k': {'name': 'WORLD'},
    }, encoding='utf-8'))
    response = msgpack.unpackb(socket.recv(), encoding='utf-8')
    assert response == {'r': 'Hello, WORLD!'}

    socket.send(msgpack.packb({
        'm': 'method3',
        'k': {'greeting': 'HOWDY'},
    }, encoding='utf-8'))
    response = msgpack.unpackb(socket.recv(), encoding='utf-8')
    assert response == {'r': 'HOWDY, world!'}

    socket.send(msgpack.packb({
        'm': 'method3',
        'k': {'greeting': 'HOWDY', 'name': 'MAN'},
    }, encoding='utf-8'))
    response = msgpack.unpackb(socket.recv(), encoding='utf-8')
    assert response == {'r': 'HOWDY, MAN!'}

    socket.send(msgpack.packb({
        'm': 'method3',
        'a': ('hey', 'man'),
    }, encoding='utf-8'))
    response = msgpack.unpackb(socket.recv(), encoding='utf-8')
    assert response == {'r': 'hey, man!'}


def test_with_client(simple_server_client):
    client = simple_server_client

    assert client.method1() == 'Hello, world!'

    assert client.method2(u'WORLD') == u'Hello, WORLD!'
    assert client.method2(name=u'WORLD') == u'Hello, WORLD!'
    assert client.method2(name=u'Ẅøřłđ') == u'Hello, Ẅøřłđ!'

    assert client.method3('Hi', 'man') == 'Hi, man!'
    assert client.method3(greeting='Hi', name='man') == 'Hi, man!'
    assert client.method3(greeting='Hi') == 'Hi, world!'

    with pytest.raises(RemoteException):
        client.method3('HELLO', greeting='Hi')

    assert client.get_list() == ['this', 'is', 'a', 'list']
    assert client.get_dict() == {'this': 'is', 'a': 'dict'}

    with pytest.raises(RemoteException):
        client.raise_value_error()

    ## Ok, the method doesn't exist, no big deal..
    with pytest.raises(RemoteException):
        client.no_such_method()

    client.method1()  # The server must still be alive here..

    ##------------------------------------------------------------
    ## Let's try with some exceptions

    ## Invalid method
    with pytest.raises(RemoteException):
        client.does_not_exist()

    ## Invalid arguments
    with pytest.raises(RemoteException):
        client.method1('this', 'does not', 'accept arguments!')

    ## This method will raise an exception
    with pytest.raises(RemoteException):
        client.divide_by_zero()


def test_smartrpyc_multi_route(simple_server_client):
    client = simple_server_client
    assert client['route1'].method1() == 'route1-method1'
    assert client['route1'].method2() == 'route1-method2'
    assert client['route1'].method3() == 'route1-method3'
    assert client['route2'].method1() == 'route2-method1'
    assert client['route2'].method2() == 'route2-method2'
    assert client['route2'].method3() == 'route2-method3'
    assert client['route3'].method1() == 'route3-method1'

    with pytest.raises(RemoteException):
        client['doesnotexist'].my_method()

    with pytest.raises(RemoteException):
        client['route1'].doesnotexist()


## Concurrency is a separate topic, and is not supported yet!

# def test_concurrent_calls(random_socket, simple_server):
#     pytest.skip()
#     server_thread = ServerProcessThread(simple_server, random_socket)
#     server_thread.start()

#     with Client(random_socket) as client1, \
#             Client(random_socket) as client2, \
#             Client(random_socket) as client3, \
#             Client(random_socket) as client4, \
#             Client(random_socket) as client5, \
#             Client(random_socket) as client6:
#         clients = list(enumerate([
#             client1, client2, client3, client4, client5, client6]))

#         ## Send requests in random order
#         random.shuffle(clients)
#         for i, client in clients:
#             socket = client._socket
#             socket.send(msgpack.packb({
#                 'm': 'method2',
#                 'a': ['socket {0}'.format(i)],
#             }, encoding='utf-8'))

#         ## Get responses in random order, and check responses
#         random.shuffle(clients)
#         for i, client in clients:
#             socket = client._socket
#             response = msgpack.unpackb(socket.recv(), encoding='utf-8')
#             assert response == {'r': 'Hello, socket {0}!'.format(i)}
