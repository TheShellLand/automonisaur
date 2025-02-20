import unittest

from automon.helpers.loggingWrapper import LoggingClient


class MyTestCase(unittest.TestCase):
    def test_something(self):
        log = LoggingClient(name=__name__)


if __name__ == '__main__':
    unittest.main()
