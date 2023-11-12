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

        self.assertIsNone(Sleeper.seconds(0))
        self.assertIsNone(Sleeper.minute(0))
        self.assertIsNone(Sleeper.within_a_minute(0))
        self.assertIsNone(Sleeper.minutes(0))
        self.assertIsNone(Sleeper.hour(0))
        self.assertIsNone(Sleeper.hours(0))
        self.assertIsNone(Sleeper.day(0))
        self.assertIsNone(Sleeper.daily(0))
        self.assertIsNone(Sleeper.time_range(0))


if __name__ == '__main__':
    unittest.main()
