"""
Serialization utilities
"""
import json
import pickle

import msgpack
from msgpack.fallback import Unicode


__all__ = ['MsgPackSerializer', 'CustomMsgPackSerializer', 'JsonSerializer',
           'PickleSerializer']


class MsgPackSerializer(object):
    @staticmethod
    def packb(o):
        return msgpack.packb(o, encoding='utf-8')

    @staticmethod
    def unpackb(packed):
        return msgpack.unpackb(packed, encoding='utf-8')


class CustomMsgPackSerializer(object):
    """
    Custom msgpack serializer, allowing to differentiate between
    strings and blobs. It's way more inefficient thant the MsgPackSerializer,
    however, since it has to use the fallback Python-only version..
    """
    @staticmethod
    def packb(o):
        return msgpack.packb(_pack_strings(o))

    @staticmethod
    def unpackb(packed):
        return _unpack_strings(msgpack.unpackb(packed))


def _pack_strings(o):
    if isinstance(o, Unicode):
        return b"u" + o.encode('utf-8')
    elif isinstance(o, bytes):
        return b"b" + o
    elif isinstance(o, dict):
        return dict(
            (_pack_strings(k), _pack_strings(v))
            for k, v in o.iteritems())
    elif isinstance(o, (list, tuple)):
        return [_pack_strings(x) for x in o]
    else:
        return o


def _unpack_strings(o):
    if isinstance(o, bytes):
        if o[0] in (b'u', ord(b'u')):
            return o[1:].decode('utf-8')
        elif o[0] in (b'b', ord(b'b')):
            return o[1:]
        raise ValueError("Invalid string object prefix {0}!".format(o[0]))
    elif isinstance(o, dict):
        return dict(
            (_unpack_strings(k), _unpack_strings(v))
            for k, v in o.iteritems())
    elif isinstance(o, (list, tuple)):
        return [_unpack_strings(x) for x in o]
    else:
        return o


class JsonSerializer(object):
    """
    .. warning::
        We have a problem with blobs here, since all the strings
        are automatically converted to unicode...
    """
    @staticmethod
    def packb(o):
        return json.dumps(o)

    @staticmethod
    def unpackb(packed):
        return json.loads(packed)


class PickleSerializer(object):
    """
    Pickle-powered serializer

    .. warning::
        Never, ever, use this for untrusted data!! Big security risk!!
    """
    @staticmethod
    def packb(o):
        return pickle.dumps(o)

    @staticmethod
    def unpackb(packed):
        return pickle.loads(packed)
