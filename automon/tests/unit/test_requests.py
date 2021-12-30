import unittest

from automon.helpers.requests import RequestsClient
from automon.helpers.requests import RequestsConfig

r = RequestsClient()


class Client(unittest.TestCase):
    def test_get(self):
        self.assertTrue(r.get('http://1.1.1.1'))
        self.assertTrue(r.requests.get('http://1.1.1.1'))
        self.assertFalse(r.get('x://127.0.0.1'))


class Config(unittest.TestCase):
    def test_config(self):
        self.assertIsNotNone(RequestsConfig())


if __name__ == '__main__':
    unittest.main()
