"""
:author: samu
:created: 4/17/13 10:37 PM
"""

import timeit

from smartrpyc.utils.serialization import CustomMsgPackSerializer, \
    MsgPackSerializer, JsonSerializer, PickleSerializer


def run_test(packer):
    packer.unpackb(packer.packb({
        'string': "This is a strijng",
        'unicode': u"This is a unicode",
        'None': None,
        'True': True,
        'False': False,
        'List': ['str', u'unicode', 10, 10.5, None, True, False],
        'int': 1000,
        'float': 3.141592,
    }))


def run_msgpack():
    run_test(MsgPackSerializer)


def run_msgpack_custom():
    run_test(CustomMsgPackSerializer)


def run_json():
    run_test(JsonSerializer)


def run_pickle():
    run_test(PickleSerializer)


if __name__ == '__main__':
    times = {}
    funcs = ['msgpack', 'msgpack_custom', 'json', 'pickle']
    for func_name in funcs:
        times[func_name] = timeit.timeit(
            stmt='run_{}()'.format(func_name),
            setup='from __main__ import run_{}'.format(func_name),
            number=10000)
    for func_name in funcs:
        print '{}: {}'.format(func_name, times[func_name])
