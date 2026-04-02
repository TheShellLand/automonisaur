import unittest

from automon.integrations.requestsWrapper import RequestsClient
from automon.integrations.requestsWrapper import RequestsConfig

r = RequestsClient()


class Client(unittest.TestCase):
    def test_get(self):
        self.assertTrue(r.get('https://8.8.8.8'))
        self.assertTrue(r.requests.get('https://8.8.8.8'))
        self.assertRaises(Exception, r.get, ('x://127.0.0.1'))


class Config(unittest.TestCase):
    def test_config(self):
        self.assertIsNotNone(RequestsConfig())


if __name__ == '__main__':
    unittest.main()
