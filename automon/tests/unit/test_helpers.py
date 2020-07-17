import unittest

from automon.helpers.assertions import *
from automon.helpers.sleeper import *


class SleeperTest(unittest.TestCase):
    def test_Sleeper(self):
        self.assertTrue(Sleeper)
        self.assertTrue(Sleeper.seconds)
        self.assertTrue(Sleeper.minute)
        self.assertTrue(Sleeper.within_a_minute)
        self.assertTrue(Sleeper.minutes)
        self.assertTrue(Sleeper.hour)
        self.assertTrue(Sleeper.hours)
        self.assertTrue(Sleeper.day)
        self.assertTrue(Sleeper.daily)
        self.assertTrue(Sleeper.time_range)

        with self.assertRaises(TypeError):
            Sleeper.seconds()
            Sleeper.seconds('1')
            Sleeper.minute()
            Sleeper.within_a_minute()
            Sleeper.minutes()
            Sleeper.hour()
            Sleeper.hours()
            Sleeper.day()
            Sleeper.daily()
            Sleeper.time_range()

        self.assertIsNone(Sleeper.seconds(SleeperTest, 0))
        self.assertIsNone(Sleeper.minute(SleeperTest, 0))
        self.assertIsNone(Sleeper.within_a_minute(SleeperTest, 0))
        self.assertIsNone(Sleeper.minutes(SleeperTest, 0))
        self.assertIsNone(Sleeper.hour(SleeperTest, 0))
        self.assertIsNone(Sleeper.hours(SleeperTest, 0))
        self.assertIsNone(Sleeper.day(SleeperTest, 0))
        self.assertIsNone(Sleeper.daily(SleeperTest, 0))
        self.assertIsNone(Sleeper.time_range(SleeperTest, 0))


class AssertionsTest(unittest.TestCase):
    def test_make_tuple(self):
        self.assertTupleEqual(make_tuple('"test",'), ('test',))
        self.assertTupleEqual(make_tuple('"test","test"'), ('test', 'test'))
        self.assertRaises(ValueError, make_tuple, 'test')
        self.assertRaises(ValueError, make_tuple, 'test,')
        self.assertRaises(ValueError, make_tuple, 'test,test')

    def test_assert_label(self):
        self.assertEqual(assert_label(':test'), ':`test`')
        self.assertIsNone(assert_label('1test'))
        self.assertEqual(assert_label('works'), ':`works`')

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

# if __name__ == '__main__':
#     unittest.main()
