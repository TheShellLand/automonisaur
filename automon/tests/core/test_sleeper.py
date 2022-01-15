import unittest

from automon.helpers.sleeper import Sleeper


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


if __name__ == '__main__':
    unittest.main()
