import unittest

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class LoggingTest(unittest.TestCase):

    def test_error(self):
        self.assertIsNone(logger.error('test'))

    def test_debug(self):
        self.assertIsNone(logger.debug('test'))

    def test_info(self):
        self.assertIsNone(logger.info('test'))

    def test_critical(self):
        self.assertIsNone(logger.critical('test'))

    def test_warn(self):
        self.assertIsNone(logger.warning('test'))


if __name__ == '__main__':
    unittest.main()
