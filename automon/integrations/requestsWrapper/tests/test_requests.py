import unittest

from automon.integrations.requestsWrapper import RequestsClient
from automon.integrations.requestsWrapper import RequestsConfig

r = RequestsClient()


class Client(unittest.TestCase):
    def test_get(self):
        r.get('https://1.1.1.1')
        r.requests.get('https://1.1.1.1')
        self.assertFalse(r.get('x://127.0.0.1'))


class Config(unittest.TestCase):
    def test_config(self):
        self.assertIsNotNone(RequestsConfig())


if __name__ == '__main__':
    unittest.main()
