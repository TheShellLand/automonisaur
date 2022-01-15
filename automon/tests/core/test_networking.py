import unittest

from automon.helpers.networking import *


class NetworkingTest(unittest.TestCase):
    def test_Networking(self):
        self.assertTrue(Networking)

    def test_check_connection(self):
        self.assertFalse(Networking.check_connection('x://localhost:0'))
        self.assertFalse(Networking.check_connection('localhost:0'))
        self.assertFalse(Networking.check_connection('localhost:0', timeout=0))

        if Networking.check_connection('x://1.1.1.1:443'):
            self.assertTrue(Networking.check_connection('https://www.google.com:443'))
            self.assertTrue(Networking.check_connection('x://www.google.com:443'))

    def test_urlparse(self):
        self.assertTrue(Networking.urlparse('x://localhost:0'))


if __name__ == '__main__':
    unittest.main()
