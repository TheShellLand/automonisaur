import unittest

from automon.helpers.assertions import *
from automon.helpers.sleeper import *
from automon.helpers.sanitation import *


class SanitationTest(unittest.TestCase):
    def test_Sanitation(self):
        self.assertTrue(Sanitation)
        self.assertTrue(Sanitation.strip_quotes)
        self.assertTrue(Sanitation.strip_spaces)
        self.assertTrue(Sanitation.strip_spaces_from_list)
        self.assertTrue(Sanitation.safe_string)
        self.assertTrue(Sanitation.dedup)
        self.assertTrue(Sanitation.list_from_string)

        self.assertRaises(TypeError, Sanitation.strip_quotes)
        self.assertRaises(TypeError, Sanitation.strip_spaces)
        self.assertRaises(TypeError, Sanitation.strip_spaces_from_list)
        self.assertRaises(TypeError, Sanitation.safe_string)
        self.assertRaises(TypeError, Sanitation.dedup)
        self.assertRaises(TypeError, Sanitation.list_from_string)

        self.assertEqual(Sanitation.strip_quotes('test'), 'test')
        self.assertEqual(Sanitation.strip_spaces(' t e s t '), 't e s t')
        self.assertEqual(Sanitation.strip_spaces(' t e s t '), 't e s t')
        self.assertEqual(Sanitation.strip_spaces_from_list(
            [' t e s t ']), ['t e s t'])
        self.assertEqual(Sanitation.safe_string(
            'a;skdfjAS*&D)(&!H!:@JEN'), 'a_skdfjAS__D____H___JEN')
        self.assertEqual(Sanitation.dedup(
            [1, 1, 'AAAAA', 'AAAAA', 'AA', 555, 555, 5555, 6666, 7, 8, 33, 1, 1232, 499124, 'a']),
            [1, 'AAAAA', 'AA', 555, 5555, 6666, 7, 8, 33, 1232, 499124, 'a'])

        self.assertEqual(Sanitation.list_from_string(
            'a,d,a,3,1,5,g,2,,a,4,1,,h,4,1,k,z'),
            ['a', 'd', 'a', '3', '1', '5', 'g', '2', '', 'a', '4', '1', '', 'h', '4', '1', 'k', 'z']
        )
        self.assertEqual(Sanitation.list_from_string(
            'a d a 3 1 5 g 2  a 4 1  h 4 1 k z'),
            ['a', 'd', 'a', '3', '1', '5', 'g', '2', '', 'a', '4', '1', '', 'h', '4', '1', 'k', 'z']
        )
        self.assertEqual(Sanitation.list_from_string(
            ' ada315g2a41h41kz '),
            ['ada315g2a41h41kz']
        )


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

        self.assertRaises(TypeError, Sleeper.seconds)
        self.assertRaises(TypeError, Sleeper.minute)
        self.assertRaises(TypeError, Sleeper.within_a_minute)
        self.assertRaises(TypeError, Sleeper.minutes)
        self.assertRaises(TypeError, Sleeper.hour)
        self.assertRaises(TypeError, Sleeper.hours)
        self.assertRaises(TypeError, Sleeper.day)
        self.assertRaises(TypeError, Sleeper.daily)
        self.assertRaises(TypeError, Sleeper.time_range)
        self.assertRaises(TypeError, Sleeper.seconds, '1')

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
