import unittest

from automon import Logging
from automon.integrations.sentryio.client import SentryClient


class CallbackTest(unittest.TestCase):
    sentry = SentryClient()
    log = Logging(name=__name__, level=Logging.DEBUG)
    log.callbacks.append(sentry)

    def test_sentry(self):
        self.assertTrue(self.log)
        self.assertTrue(self.log.info('LOG'))
        self.assertTrue(self.log.debug('LOG'))
        self.assertTrue(self.log.error('LOG'))
        self.assertTrue(self.log.warn('LOG'))
        self.assertTrue(self.log.critical('LOG'))
        pass


if __name__ == '__main__':
    unittest.main()
