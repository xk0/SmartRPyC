"""
Serialization utilities
"""
import json
import pickle

import msgpack


__all__ = ['MsgPackSerializer', 'CustomMsgPackSerializer', 'JsonSerializer',
           'PickleSerializer']


class MsgPackSerializer(object):
    """
    Messagepack-based serializer.
    Thanks to the new features added in msgpack, we now support
    binary vs unicode strings natively, and other nice things.
    """

    @staticmethod
    def packb(o):
        #return msgpack.packb(o, encoding='utf-8')
        msgpack_packer = msgpack.Packer(encoding='utf-8', use_bin_type=True)
        return msgpack_packer.pack(o)

    @staticmethod
    def unpackb(packed):
        #return msgpack.unpackb(packed, encoding='utf-8')
        msgpack_unpacker = msgpack.Unpacker(encoding='utf-8')
        msgpack_unpacker.feed(packed)
        return msgpack_unpacker.unpack()


## For backwards compatibility.
## This is now deprecated in favor of standard
## MsgPackSerializer.
CustomMsgPackSerializer = MsgPackSerializer


class JsonSerializer(object):
    """
    .. warning::
        We have a problem with blobs here, since all the strings
        are automatically converted to unicode...
    """
    @staticmethod
    def packb(o):
        return json.dumps(o).encode('utf-8')

    @staticmethod
    def unpackb(packed):
        return json.loads(packed.decode('utf-8'))


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
