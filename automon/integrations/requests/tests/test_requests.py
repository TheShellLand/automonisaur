import unittest

from automon.integrations.requests import RequestsClient
from automon.integrations.requests import RequestsConfig

r = RequestsClient()


class Client(unittest.TestCase):
    def test_get(self):
        self.assertTrue(r.get('https://1.1.1.1'))
        self.assertTrue(r.requests.get('https://1.1.1.1'))
        self.assertFalse(r.get('x://127.0.0.1'))


class Config(unittest.TestCase):
    def test_config(self):
        self.assertIsNotNone(RequestsConfig())


if __name__ == '__main__':
    unittest.main()
