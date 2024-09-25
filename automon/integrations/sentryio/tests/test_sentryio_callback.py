import unittest

from automon import log
from automon.integrations.sentryio.client import SentryClient

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)
sentry = SentryClient()


class CallbackTest(unittest.TestCase):

    def test_sentry(self):
        self.assertIsNone(logger.info('test'))
        self.assertIsNone(logger.debug('test'))
        self.assertIsNone(logger.error('test'))
        self.assertIsNone(logger.warning('test'))
        self.assertIsNone(logger.critical('test'))


if __name__ == '__main__':
    unittest.main()
