import unittest

from datetime import datetime

from automon.integrations.sentryio import SentryClient
from automon.integrations.geoip import Geoip

from automon.log import Logging


class SentryClientTest(unittest.TestCase):
    def test_sentry(self):
        s = SentryClient()
        l = Logging()

        if s.isConnected():
            self.assertTrue(s.capture_exception(Exception(f'test capture_exception')))
            self.assertTrue(s.capture_message(f'test capture_message'))
            # self.assertTrue(s.capture_event('test capture_event', 'warning'))
            self.assertTrue(l.info(f'test log info'))
            self.assertTrue(l.debug(f'test log debug'))
            self.assertTrue(l.warning(f'test log warning'))
            self.assertTrue(l.error(f'test log error'))
            self.assertTrue(l.critical(f'test log critical'))


if __name__ == '__main__':
    unittest.main()
