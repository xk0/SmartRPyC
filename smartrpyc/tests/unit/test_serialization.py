# coding=utf-8
"""
Tests for serialization
"""


class TestSerialization(object):
    def _run_serialization_tests(self, packer, support_bytes=True):
        test_values = [
            ## These should present no significant problems!
            'Hello, world!',
            ['hello', 'world'],
            {'Hello': 'world'},
            {'Hello': 'world', 'Hello2': 'world2'},
            {'hello': ['w', 'o', 'r', 'l', 'd']},
            True, False, None,
            (2 ** 64) - 1,  # MAXINT (64bit) <-- Beware!
            10, 1.0, 0.2, -100000, -10.5,
            u"This is a unicode string",
            ['This is', u'a mixed', 'list'],
            u"Hélló wórld ¶¬¹²³¤€˛¡¿",
            {"this": u"is", "a": u"díctíöñáry"},
            {
                'ok, we can even do this': [
                    u"Hello, world!",
                    u"Hëllö, wørlḋ",
                    ['Hello', 'world'],
                ],
                u"And this??": {'yay': 'hello'},
                u"øf cøürsë, wé cán..": True,
                "ready?": [
                    10, 9, 8, 7, 6, 5, 5.5, 5.4, 5.3, 5.2, "Boom!", None,
                ],
            },
            u"\u1234\u5678 <-- this is... something!",
            u"What's this \x01 \x02 \x03 \x80\x81\x92\x93 crap??",
        ]

        ## These should work only with msgpack_custom and pickle
        extended_test_values = [
            "\x01\x02\x03\x04\x05\x06",
            b"And this is \x00\x01\x02\x03 a py3k \x80\x81\x82\x83 binary",
        ]

        if support_bytes:
            test_values += extended_test_values

        for value in test_values:
            _new_value = packer.unpackb(packer.packb(value))
            assert value == _new_value
            if support_bytes:
                assert type(value) == type(_new_value)

    def test_serialization_msgpack(self):
        from smartrpyc.utils.serialization import MsgPackSerializer
        self._run_serialization_tests(MsgPackSerializer, support_bytes=False)

    def test_serialization_msgpack_custom(self):
        from smartrpyc.utils.serialization import CustomMsgPackSerializer
        self._run_serialization_tests(CustomMsgPackSerializer)

    def test_serialization_json(self):
        from smartrpyc.utils.serialization import JsonSerializer
        self._run_serialization_tests(JsonSerializer, support_bytes=False)

    def test_serialization_pickle(self):
        from smartrpyc.utils.serialization import PickleSerializer
        self._run_serialization_tests(PickleSerializer)
