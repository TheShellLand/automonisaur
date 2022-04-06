import unittest

from automon.log.logger import Logging, LogStream


class LoggingTest(unittest.TestCase):
    log = Logging()

    def test_logger(self):
        self.assertTrue(self.log)

    def test_error(self):
        self.assertTrue(self.log.error('test'))

    def test_debug(self):
        self.assertTrue(self.log.debug('test'))

    def test_info(self):
        self.assertTrue(self.log.info('test'))

    def test_critical(self):
        self.assertTrue(self.log.critical('test'))

    def test_warn(self):
        self.assertTrue(self.log.warning('test'))
        with self.assertRaises(Exception):
            self.log.error(raise_exception=True)

    def test_now(self):
        self.assertTrue(self.log.now())

    def test_delta(self):
        self.assertTrue(self.log.uptime())


class LogStreamTest(unittest.TestCase):
    stream = LogStream()

    def test_stream(self):
        self.assertTrue(self.stream)

    def test_repr(self):
        self.assertFalse(f'{self.stream}')

    def test_flush(self):
        self.assertIsNone(self.stream.flush())

    def test_write(self):
        self.assertIsNone(self.stream.write('test'))


if __name__ == '__main__':
    unittest.main()
