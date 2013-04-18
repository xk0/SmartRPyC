"""
:author: samu
:created: 4/17/13 10:37 PM
"""

import timeit

from smartrpyc.utils import serialization
import msgpack


def run_test(module):
    module.unpackb(module.packb({
        'string': "This is a strijng",
        'unicode': u"This is a unicode",
        'None': None,
        'True': True,
        'False': False,
        'List': ['str', u'unicode', 10, 10.5, None, True, False],
        'int': 1000,
        'float': 3.141592,
    }))


def run_vanilla():
    run_test(msgpack)


def run_custom():
    run_test(serialization)


if __name__ == '__main__':
    time1 = timeit.timeit(stmt='run_vanilla()',
                          setup='from __main__ import run_vanilla',
                          number=100000)
    time2 = timeit.timeit(stmt='run_custom()',
                          setup='from __main__ import run_custom',
                          number=100000)
    print time1
    print time2
