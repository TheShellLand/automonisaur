import unittest
import asyncio

from datetime import datetime

from automon import log
from automon.integrations.sentryio import SentryClient
from automon.integrations.geoip import Geoip

s = SentryClient()


class SentryClientTest(unittest.TestCase):
    async def test_sentry(self):
        if await s.isConnected():
            self.assertTrue(asyncio.run(s.capture_exception(Exception(f'test capture_exception'))))
            self.assertTrue(asyncio.run(s.capture_message(f'test capture_message')))
            # self.assertTrue(asyncio.run(s.capture_event('test capture_event', 'warning')))


if __name__ == '__main__':
    unittest.main()
