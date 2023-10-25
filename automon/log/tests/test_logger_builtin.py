import unittest

from automon.log import logger

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class LoggingTest(unittest.TestCase):

    def test_logger(self):
        self.assertTrue(log)

    def test_error(self):
        self.assertIsNone(log.error('test'))

    def test_debug(self):
        self.assertIsNone(log.debug('test'))

    def test_info(self):
        self.assertIsNone(log.info('test'))

    def test_critical(self):
        self.assertIsNone(log.critical('test'))

    def test_warn(self):
        self.assertIsNone(log.warning('test'))


if __name__ == '__main__':
    unittest.main()
