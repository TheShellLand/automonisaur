import unittest

from automon.integrations.instagram.client_browser import InstagramBrowserClient

c = InstagramBrowserClient()


class InstagramClientTest(unittest.TestCase):
    if c.authenticate():
        def test_authenticate(self):
            self.assertTrue(c.authenticate())


if __name__ == '__main__':
    unittest.main()
