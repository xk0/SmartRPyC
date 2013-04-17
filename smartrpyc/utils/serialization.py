"""
Serialization utilities
"""

# from msgpack import Packer, Unpacker, pack
import struct
import msgpack.fallback
from msgpack.exceptions import PackValueError, ExtraData
from msgpack.fallback import DEFAULT_RECURSE_LIMIT, int_types, Unicode, \
    dict_iteritems


def pack(o, stream, default=None, encoding='utf-8', unicode_errors='strict'):
    """ Pack object `o` and write it to `stream` """
    packer = Packer(default=default, encoding=encoding,
                    unicode_errors=unicode_errors)
    stream.write(packer.pack(o))


def packb(o, default=None, encoding='utf-8', unicode_errors='struct',
          use_single_float=False):
    """ Pack object `o` and return packed bytes """
    packer = Packer(default=default,
                    encoding=encoding,
                    unicode_errors=unicode_errors,
                    use_single_float=use_single_float)
    return packer.pack(o)


def unpack(stream, object_hook=None, list_hook=None, use_list=True,
           encoding=None, unicode_errors='strict',
           object_pairs_hook=None):
    """ Unpack an object from `stream`.

    Raises `ExtraData` when `stream` has extra bytes. """
    unpacker = Unpacker(stream, object_hook=object_hook, list_hook=list_hook,
                        use_list=use_list,
                        encoding=encoding, unicode_errors=unicode_errors,
                        object_pairs_hook=object_pairs_hook)
    ret = unpacker._fb_unpack()
    if unpacker._fb_got_extradata():
        raise ExtraData(ret, unpacker._fb_get_extradata())
    return ret


def unpackb(packed, object_hook=None, list_hook=None, use_list=True,
            encoding=None, unicode_errors='strict',
            object_pairs_hook=None):
    """ Unpack an object from `packed`.

    Raises `ExtraData` when `packed` contains extra bytes. """
    unpacker = Unpacker(None, object_hook=object_hook, list_hook=list_hook,
                        use_list=use_list,
                        encoding=encoding, unicode_errors=unicode_errors,
                        object_pairs_hook=object_pairs_hook)
    unpacker.feed(packed)
    ret = unpacker._fb_unpack()
    if unpacker._fb_got_extradata():
        raise ExtraData(ret, unpacker._fb_get_extradata())
    return ret


class Packer(msgpack.fallback.Packer):
    def _pack(self, obj, *args, **kwargs):

        if isinstance(obj, Unicode):
            obj = "u" + obj.encode('utf-8')

        elif isinstance(obj, bytes):
            obj = "b" + obj

        return super(Packer, self)._pack(obj, *args, **kwargs)


class Unpacker(msgpack.fallback.Unpacker):
    def _fb_unpack(self, *args, **kwargs):
        data = super(Unpacker, self)._fb_unpack(*args, **kwargs)
        if isinstance(data, bytes):
            if data[0] == 'u':
                return data[1:].decode('utf-8')
            elif data[0] == 'b':
                return data[1:]
            raise ValueError("Invalid string object prefix {}!".format(data[0]))
        return data
