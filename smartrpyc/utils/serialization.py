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
        # packer = CustomPacker()
        # return packer.pack(o)

    @staticmethod
    def unpackb(packed):
        return _unpack_strings(msgpack.unpackb(packed))
        # unpacker = CustomUnpacker(None)
        # unpacker.feed(packed)
        # ret = unpacker._fb_unpack()
        # if unpacker._fb_got_extradata():
        #     raise ExtraData(ret, unpacker._fb_get_extradata())
        # return ret


def _pack_strings(o):
    if isinstance(o, Unicode):
        return "u" + o.encode('utf-8')
    elif isinstance(o, bytes):
        return "b" + o
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
        if o[0] == 'u':
            return o[1:].decode('utf-8')
        elif o[0] == 'b':
            return o[1:]
        raise ValueError("Invalid string object prefix {}!".format(o[0]))
    elif isinstance(o, dict):
        return dict(
            (_unpack_strings(k), _unpack_strings(v))
            for k, v in o.iteritems())
    elif isinstance(o, (list, tuple)):
        return [_unpack_strings(x) for x in o]
    else:
        return o


# class CustomPacker(msgpack.fallback.Packer):
#     def _pack(self, obj, *args, **kwargs):
#
#         if isinstance(obj, Unicode):
#             obj = "u" + obj.encode('utf-8')
#
#         elif isinstance(obj, bytes):
#             obj = "b" + obj
#
#         return super(CustomPacker, self)._pack(obj, *args, **kwargs)
#
#
# class CustomUnpacker(msgpack.fallback.Unpacker):
#     def _fb_unpack(self, *args, **kwargs):
#         data = super(CustomUnpacker, self)._fb_unpack(*args, **kwargs)
#         if isinstance(data, bytes):
#             if data[0] == 'u':
#                 return data[1:].decode('utf-8')
#             elif data[0] == 'b':
#                 return data[1:]
#             raise ValueError("Invalid string object prefix {}!".format(data[0]))
#         return data


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
