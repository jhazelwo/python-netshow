#!/usr/bin/env python
""" -*- coding: utf-8 -*-
Unit tests for python-netshow.
Testing saves lives!

Hint:
# PYTHONPATH=`pwd` python tests.py

Not a lot of test methods for unittest in Python 2.6.6 :(
>>> dir(unittest.TestCase)
['__call__', '__class__', '__delattr__', '__dict__', '__doc__', '__eq__',
'__format__', '__getattribute__', '__hash__', '__init__', '__module__',
'__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
'__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_exc_info',
'assertAlmostEqual', 'assertAlmostEquals', 'assertEqual', 'assertEquals',
'assertFalse', 'assertNotAlmostEqual', 'assertNotAlmostEquals',
'assertNotEqual', 'assertNotEquals', 'assertRaises', 'assertTrue', 'assert_',
'countTestCases', 'debug', 'defaultTestResult', 'fail', 'failIf',
'failIfAlmostEqual', 'failIfEqual', 'failUnless', 'failUnlessAlmostEqual',
'failUnlessEqual', 'failUnlessRaises', 'failureException', 'id', 'run',
'setUp', 'shortDescription', 'tearDown']
>>>

"""
from unittest import TestCase, main
from netshow import NetShow, RegexError

INPUT = [
{'protocol': 'tcp', 'local_port': '22', 'pid': '1101', 'remote_port': '*', 'local_ip': '0.0.0.0', 'state': 'LISTEN', 'program': '/usr/sbin/sshd', 'remote_ip': '0.0.0.0'},
{'protocol': 'tcp', 'local_port': '22', 'pid': '13269', 'remote_port': '54101', 'local_ip': '172.28.142.138', 'state': 'ESTABLISHED', 'program': '/usr/sbin/sshd', 'remote_ip': '192.168.162.33'},
{'protocol': 'udp', 'local_port': '123', 'pid': '1109', 'remote_port': '*', 'local_ip': '172.28.142.138', 'state': '', 'program': '/usr/sbin/ntpd', 'remote_ip': '0.0.0.0'},
{'protocol': 'udp', 'local_port': '123', 'pid': '1109', 'remote_port': '*', 'local_ip': '127.0.0.1', 'state': '', 'program': '/usr/sbin/ntpd', 'remote_ip': '0.0.0.0'},
{'protocol': 'udp', 'local_port': '123', 'pid': '1109', 'remote_port': '*', 'local_ip': '0.0.0.0', 'state': '', 'program': '/usr/sbin/ntpd', 'remote_ip': '0.0.0.0'},
{'protocol': 'tcp6', 'local_port': '22', 'pid': '1101', 'remote_port': '*', 'local_ip': '::', 'state': 'LISTEN', 'program': '/usr/sbin/sshd', 'remote_ip': '::'},
{'protocol': 'udp6', 'local_port': '123', 'pid': '1109', 'remote_port': '*', 'local_ip': 'fe80::250:56ff:feb1:69bd', 'state': '', 'program': '/usr/sbin/ntpd', 'remote_ip': '::'},
{'protocol': 'udp6', 'local_port': '123', 'pid': '1109', 'remote_port': '*', 'local_ip': '::1', 'state': '', 'program': '/usr/sbin/ntpd', 'remote_ip': '::'},
{'protocol': 'udp6', 'local_port': '123', 'pid': '1109', 'remote_port': '*', 'local_ip': '::', 'state': '', 'program': '/usr/sbin/ntpd', 'remote_ip': '::'}
]


class TestInit(TestCase):
    """ def __init__(self): """
    def test_init(self):
        instance = NetShow()
        self.assertFalse(isinstance(instance, TestCase))
        self.assertTrue(isinstance(instance, NetShow))

    def test_default_attributes(self):
        instance = NetShow()
        self.assertFalse(instance.as_json)
        self.assertFalse(instance.as_dict)
        self.assertTrue(instance.use_header)

class TestUsage(TestCase):
    """ def usage(self): """
    def test_usage(self):
        instance = NetShow()
        self.assertFalse('BROKEN = True' in instance.usage())
        self.assertTrue('netshow.py, version 1.0' in instance.usage())

class TestSearchDictValues(TestCase):
    """ def search_dict_values(self, pattern, d): """
    def test_search_dict_values(self):
        instance = NetShow()
        method = instance.search_dict_values
        self.assertRaises(RegexError, method, '*', INPUT[0])
        self.assertFalse(method('pattern', INPUT[0]))
        self.assertEquals(method('tcp', INPUT[0]), INPUT[0])
        self.assertTrue(method('tcp', INPUT[0]))
        self.assertTrue(method('tcp|.*sshd$', INPUT[0]))
        self.assertTrue(method('0.0.0.0', INPUT[0]))
        self.assertTrue(method('1101', INPUT[0]))
        self.assertTrue(method('\*', INPUT[0]))
        self.assertTrue(method('LISTEN', INPUT[0]))
        self.assertTrue(method('.*', INPUT[0]))

class TestMatchAllNeedles(TestCase):
    """ def match_all_needles(self, needle, haystack): """
    def test_match_all_needles(self):
        instance = NetShow()
        method = instance.match_all_needles
        self.assertFalse(method(['4101','972.28.142.138', 'udp|80'], INPUT[1]))
        self.assertTrue(method(['54101','172.28.142.138', 'tcp|22'], INPUT[1]))

class TestFilter(TestCase):
    """ def filter(self, params): """
    def test_filter(self):
        instance = NetShow()
        instance.contents = INPUT
        method = instance.filter
        self.assertTrue(method([]))
        self.assertFalse(method(['nope', 'cant|match|this', 80]))
        self.assertTrue(method(['54101','172.28.142.138', 'tcp|22']))
        self.assertEquals(instance.results, [INPUT[1]])

    def test_filter_int(self):
        instance = NetShow()
        instance.contents = INPUT
        method = instance.filter
        self.assertFalse(method([80]))
        self.assertTrue(method([22]))

class TestLintToDict(TestCase):
    """ def line_to_dict(self, line, protocol) """
    def test_line_to_dict_tcp(self):
        instance = NetShow()
        instance.contents = INPUT
        method = instance.line_to_dict
        line = '   0: 00000000:0016 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 9479 1 ffff880139ba5480 99 0 0 10 -1'
        self.assertNotEquals(method(line, 'tcp'), INPUT[1])
        self.assertEquals(method(line, 'tcp'), INPUT[0])

    def test_line_to_dict_udp6(self):
        instance = NetShow()
        instance.contents = INPUT
        method = instance.line_to_dict
        line = '  16: 000080FE00000000FF565002BD69B1FE:007B 00000000000000000000000000000000:0000 07 00000000:00000000 00:00000000 00000000     0        0 9523 2 ffff880139b50400 0'
        self.assertNotEquals(method(line, 'udp6'), INPUT[1])
        self.assertEquals(method(line, 'udp6'), INPUT[6])

class TestProcToDict(TestCase):
    """ def proc_to_dict(self, protocol): """
    def test_proc_to_dict(self):
        instance = NetShow()
        # instance.contents = INPUT
        method = instance.proc_to_dict
        self.assertTrue(isinstance(method('tcp'), list))
        self.assertTrue(isinstance(method('udp'), list))
        self.assertTrue(isinstance(method('tcp')[0], dict))
        self.assertTrue(isinstance(method('udp')[0], dict))

class TestConvertIP(TestCase):
    """ def _convert_ip(self, address): """
    def test_convert_ip(self):
        instance = NetShow()
        method = instance._convert_ip
        self.assertEquals(method('00000000000000000000000000000000'), '::')
        self.assertEquals(method('000080FE00000000FF565002BD69B1FE'), 'fe80::250:56ff:feb1:69bd')
        self.assertEquals(method('00000000'), '0.0.0.0')
        self.assertEquals(method('8A8E1CAC'), '172.28.142.138')

class TestHex2Dec(TestCase):
    """ def _hex2dec(self, this): """
    def test_hex2dec(self):
        instance = NetShow()
        method = instance._hex2dec
        self.assertEquals(method('00'), '0')
        self.assertEquals(method('007B'), '123')
        self.assertEquals(method('0016'), '22')

class TestRemoveEmpty(TestCase):
    """ def _remove_empty(self, this): """
    def test_remove_empty(self):
        instance = NetShow()
        method = instance._remove_empty
        self.assertNotEquals(method(['bob', ' ', 'pat', '']), ['bob', 'pat'])
        self.assertEquals(method(['bob', '', 'pat', '']), ['bob', 'pat'])

class TestConvertIPPort(TestCase):
    """ def _convert_ip_port(self, array): """
    def test_convert_ip_port(self):
        instance = NetShow()
        method = instance._convert_ip_port
        self.assertNotEquals(method('8A8E1CAC:007B'), ('fe80::250:56ff:feb1:69bd', '22'))
        self.assertNotEquals(method('000080FE00000000FF565002BD69B1FE:0016'), ('172.28.142.138', '123'))
        self.assertEquals(method('000080FE00000000FF565002BD69B1FE:0016'), ('fe80::250:56ff:feb1:69bd', '22'))
        self.assertEquals(method('8A8E1CAC:007B'), ('172.28.142.138', '123'))



if __name__ == '__main__':
    main()
