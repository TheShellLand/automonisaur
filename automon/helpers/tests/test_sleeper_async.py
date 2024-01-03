import unittest
import asyncio

from automon.helpers.sleeper import Sleeper


class SleeperTest(unittest.TestCase):
    def test_Sleeper(self):
        loop = asyncio.new_event_loop()
        task = loop.run_until_complete(Sleeper.seconds_async(1))


if __name__ == '__main__':
    unittest.main()
