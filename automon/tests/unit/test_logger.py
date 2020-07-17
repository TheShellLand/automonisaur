import unittest

from automon.log.logger import Logging, LogStream


class LoggerTest(unittest.TestCase):

    def test_logger(self):
        self.assertTrue(Logging())
        self.assertIsNone(Logging().error('test'))
        self.assertIsNone(Logging().debug('test'))
        self.assertIsNone(Logging().info('test'))
        self.assertIsNone(Logging().critical('test'))
        self.assertIsNone(Logging().warning('test'))

    def test_logstream(self):
        self.assertTrue(LogStream())
        self.assertFalse(f'{LogStream()}')
        self.assertIsNone(LogStream().flush())
        self.assertIsNone(LogStream().write('test'))

# if __name__ == '__main__':
#     unittest.main()
