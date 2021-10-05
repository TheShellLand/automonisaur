import unittest

from automon.helpers.assertions import *
from automon.helpers.regex import *


class RegexTest(unittest.TestCase):

    def test_magic(self):
        self.assertTrue(Magic)
        test = '100.15.96.234 helehleeajd'
        self.assertTrue(Magic.magic_box(test))

    def test_geolocation(self):
        self.assertTrue(geolocation)


class AssertionsTest(unittest.TestCase):
    def test_make_tuple(self):
        self.assertTupleEqual(make_tuple('"test",'), ('test',))
        self.assertTupleEqual(make_tuple('"test","test"'), ('test', 'test'))
        self.assertRaises(ValueError, make_tuple, 'test')
        self.assertRaises(ValueError, make_tuple, 'test,')
        self.assertRaises(ValueError, make_tuple, 'test,test')

    def test_assert_tuple(self):
        self.assertFalse(assert_tuple('test'))
        self.assertFalse(assert_tuple(1))
        self.assertFalse(assert_tuple(None))
        self.assertFalse(assert_tuple(object))
        self.assertFalse(assert_tuple(''))
        self.assertFalse(assert_tuple({}))
        self.assertFalse(assert_tuple(('test')))
        self.assertFalse(assert_tuple({1: 2}))
        self.assertTrue(assert_tuple(()))
        self.assertTrue(assert_tuple(('test',)))

    def test_assert_dict(self):
        self.assertFalse(assert_dict('test'))
        self.assertFalse(assert_dict({'test'}))
        self.assertTrue(assert_dict({'test': 'test'}))

    def test_assert_list(self):
        self.assertFalse(assert_list('test'))
        self.assertTrue(assert_list(['test']))
        self.assertTrue(assert_list([]))

    def test_assert_string(self):
        self.assertFalse(assert_string([]))
        self.assertFalse(assert_string(1))
        self.assertFalse(assert_string({}))
        self.assertFalse(assert_string(dict()))
        self.assertFalse(assert_string(tuple()))
        self.assertRaises(TypeError, assert_string)
        self.assertTrue(assert_string('test'))


if __name__ == '__main__':
    unittest.main()
