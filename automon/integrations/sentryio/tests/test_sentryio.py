import unittest

from datetime import datetime

from automon import log
from automon.integrations.sentryio import SentryClient
from automon.integrations.geoip import Geoip

s = SentryClient()


class SentryClientTest(unittest.TestCase):
    def test_sentry(self):
        if s.isConnected():
            self.assertTrue(s.capture_exception(Exception(f'test capture_exception')))
            self.assertTrue(s.capture_message(f'test capture_message'))
            # self.assertTrue(s.capture_event('test capture_event', 'warning'))


if __name__ == '__main__':
    unittest.main()
