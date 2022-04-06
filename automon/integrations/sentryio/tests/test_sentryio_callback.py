import unittest

from automon.log import Logging
from automon.integrations.sentryio.client import SentryClient


class CallbackTest(unittest.TestCase):
    sentry = SentryClient()
    log = Logging(name=__name__, level=Logging.DEBUG)
    log.callbacks.append(sentry)

    def test_sentry(self):
        self.assertTrue(self.log)
        self.assertTrue(self.log.info('test'))
        self.assertTrue(self.log.debug('test'))
        self.assertTrue(self.log.error('test'))
        self.assertTrue(self.log.warn('test'))
        self.assertTrue(self.log.critical('test'))


if __name__ == '__main__':
    unittest.main()
