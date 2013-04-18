# coding=utf-8
"""
Tests for serialization
"""
import unittest


class SerializationTestCase(unittest.TestCase):
    def test_serialization(self):
        from smartrpyc.utils.serialization import packb, unpackb
        test_values = [
            'Hello, world!',
            ['hello', 'world'],
            {'Hello': 'world'},
            {'Hello': 'world', 'Hello2': 'world2'},
            u"This is a unicode string",
            "\x01\x02\x03\x04\x05\x06",
            ['This is', u'a mixed', 'list'],
            u"Hélló wórld ¶¬¹²³¤€˛¡¿",
            {"this": u"is", "a": u"díctíöñáry"},
            b"And this is \x00\x01\x02\x03 a py3k \x80\x81\x82\x83 binary",
            u"\u1234\u5678 <-- this is... something!",
            {
                'ok, we can even do this': [
                    u"Hello, world!",
                    u"Hëllö, wørlḋ",
                    ['Hello', b'world'],
                ],
                u"And this??": {'yay': 'hello'},
                u"øf cøürsë, wé cán..": True,
                "ready?": [
                    10, 9, 8, 7, 6, 5, 5.5, 5.4, 5.3, 5.2, "Boom!", None,
                ],
            },
            True,
            False,
            None,
            10,
            (2 ** 64) - 1,  # MAXINT (64bit) <-- Beware!
            1.0,
            0.2,
            -100000,
            -10.5,
        ]

        for value in test_values:
            _new_value = unpackb(packb(value))
            self.assertEqual(value, _new_value)
            self.assertEqual(type(value), type(_new_value))
