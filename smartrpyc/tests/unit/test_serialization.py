# coding=utf-8
"""
Tests for serialization
"""

import pytest

from smartrpyc.utils.serialization import (
    MsgPackSerializer, JsonSerializer, PickleSerializer)

# Serializers not supporting extremely-long longs
XFAIL_NO_EXTREME_LONG = (MsgPackSerializer,)

# Serializers not supporting tuples
XFAIL_NO_TUPLES = (JsonSerializer, MsgPackSerializer)

# Serializers not supporting non-string keys
XFAIL_STRING_KEYS_ONLY = (JsonSerializer,)

# Serializers not supporting "bytes" strings
XFAIL_NO_BYTES = (JsonSerializer,)


sample_payloads = [
    ## First try with some base types
    ('bytes', b'Hello, world. This is a bytes string.', XFAIL_NO_BYTES),
    ('unicode_ascii', u'Hello, world. This is a unicode string.'),
    ('unicode_utf8', u'«¿How do you say “bacon” in your language?»'),
    ('unicode_escaped', u"\u265a\u265b\u265c\u265d"),  # Chess pieces
    ('100', 100),
    ('3.1415', 3.1415),
    ('long_int', 12345678901234567890),
    ('-23', -23),
    ('-42306152', -42306152),
    ('-99.66', -99.66),
    ('MAXINT64', 2**64 - 1),
    ('-MAXINT64', -(2**63)),
    ('2**128', (2 ** 128), XFAIL_NO_EXTREME_LONG),
    ('-(2**128)', -(2 ** 128), XFAIL_NO_EXTREME_LONG),
    ('None', None),
    ('True', True),
    ('False', False),

    ## Some lists of base types
    ('list_of_bytes', [b'spam', b'eggs', b'bacon'], XFAIL_NO_BYTES),
    ('list_of_unicode_ascii', [u'spam', u'eggs', u'bacon']),
    ('list_of_unicode_utf8', [u'spâm', u'ëggs', u'bäcøn']),
    ('list_of_mixed_bytes_unicode', [
        u'spâm', b'spam', u'ëggs', b'spam', u'bäcøn', b'spam',
        b'spam', b'spam!'], XFAIL_NO_BYTES),
    ('list_of_ints', [1, 2, 3, 4]),

    ## What about tuples?
    ('tuple0', (u'aaa', u'bbb', u'ccc'), XFAIL_NO_TUPLES),
    ('tuple1', [(u'A', u'B', u'C'), (1, 2, 3), (1.1, 2.2)], XFAIL_NO_TUPLES),
    ('tuple2', (u'a', {u'A': u'B'}), XFAIL_NO_TUPLES),

    ## Some dicts of base types
    ('dict0', {b'spam': 0.22, b'eggs': 1.32, b'bacon': 1.8}, XFAIL_NO_BYTES),
    ('dict1', {u'spâm': 0.22, u'ëggs': 1.32, u'bäcøn': 1.8}),
    ('dict2',
     {b'spam': u'THIS_IS_SPAM!!', b'eggs': 1.32, b'bacon': 1.8,
      u'spâm': u'SPÄMMY-SPAM!', u'ëggs': 1.32,
      u'bäcøn': ['DE', 'LI', 'CIOUS!']},
     XFAIL_NO_BYTES),

    ## keys of different types..
    ('dict_with_nonstring_keys',
        {True: "True", None: "None", 123: "123", 3.14: "pi"},
        XFAIL_STRING_KEYS_ONLY),

    ## Mixing stuff
    ('dict_with_mixed_values', {
        'values': [1, 2, 3],
        'sub-dict': {'a': 1, 'b': 2},
        'example': u"This is a string"}),

    ## Those can cause serious issues!
    ('inv_unicode_1', u'Invalid characters in UNICODE: \x99\x88\x00\xff'),
    ('inv_unicode_2',
     b'Invalid characters in BYTES: \x99\x88\x00\xff',
     XFAIL_NO_BYTES),
    ('inv_unicode_3',
     b'Unicode in BYTES: \u265A\u265B\u265C\u265D',
     XFAIL_NO_BYTES),

    ## todo: now test with other objects, such as objects and exceptions
    ## todo: make MsgpackSerializer handle tuples (w/ about long long ints?)
]
sample_payloads_dict = dict((i[0], i[1]) for i in sample_payloads)


serializers = {
    'json': JsonSerializer,
    'msgpack': MsgPackSerializer,
    'pickle': PickleSerializer,
}


def generate_serializer_data_key_pairs():
    for serializer_id, serializer in serializers.iteritems():
        for data_item in sample_payloads:
            marker = lambda x: x
            if (len(data_item) > 2) \
               and (data_item[2] is not None) \
               and issubclass(serializer, data_item[2]):
                marker = pytest.mark.xfail
            yield marker(','.join((serializer_id, data_item[0])))


@pytest.fixture(params=list(generate_serializer_data_key_pairs()))
def serializer_data_pairs(request):
    """
    Fixture returning (serializer, data) pairs, used in tests.

    This thing is quite tricky, since we want descriptive labels
    to end up in the pytest logging output, so we need to parametrize
    on string values, and convert them from the fixture..
    """

    serializer_id, data_id = request.param.split(',')
    serializer = serializers[serializer_id]
    data = sample_payloads_dict[data_id]
    return serializer, data


def test_serialization(serializer_data_pairs):
    serializer, data = serializer_data_pairs
    packed = serializer.packb(data)
    assert isinstance(packed, bytes)
    unpacked = serializer.unpackb(packed)
    assert unpacked == data
