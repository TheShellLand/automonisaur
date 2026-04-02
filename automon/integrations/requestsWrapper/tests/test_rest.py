import unittest

from automon.integrations.requestsWrapper.rest import BaseRestClient

r = BaseRestClient()


class Client(unittest.TestCase):
    def test_get(self):
        self.assertTrue(r.get('https://8.8.8.8'))
        self.assertTrue(r.requests.get('https://8.8.8.8'))
        self.assertRaises(Exception, r.get, ('x://127.0.0.1'))


if __name__ == '__main__':
    unittest.main()
