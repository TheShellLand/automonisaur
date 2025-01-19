import unittest

from automon.integrations.requestsWrapper.rest import BaseRestClient

r = BaseRestClient()


class Client(unittest.TestCase):
    def test_get(self):
        self.assertTrue(r.get('https://1.1.1.1'))
        self.assertTrue(r.requests.get('https://1.1.1.1'))
        self.assertFalse(r.get('x://127.0.0.1'))


if __name__ == '__main__':
    unittest.main()
