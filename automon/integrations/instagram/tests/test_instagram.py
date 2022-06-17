import unittest

from automon.integrations.instagram.client import InstagramClient

c = InstagramClient()


class InstagramClientTest(unittest.TestCase):
    def test_authenticate(self):
        pass


if __name__ == '__main__':
    unittest.main()
