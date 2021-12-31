import unittest

from datetime import datetime

from automon.integrations import SentryClient
from automon.integrations.geoip import Geoip

from automon import Logging


class SentryClientTest(unittest.TestCase):
    def test_sentry(self):
        s = SentryClient()
        l = Logging()

        if s.isConnected():
            self.assertTrue(s.capture_exception(Exception(f'test capture_exception')))
            self.assertTrue(s.capture_message(f'test capture_message'))
            # self.assertTrue(s.capture_event('test capture_event', 'warning'))
            self.assertIsNone(l.info(f'test log info'))
            self.assertIsNone(l.debug(f'test log debug'))
            self.assertIsNone(l.warning(f'test log warning'))
            self.assertIsNone(l.error(f'test log error'))
            self.assertIsNone(l.critical(f'test log critical'))


if __name__ == '__main__':
    unittest.main()
