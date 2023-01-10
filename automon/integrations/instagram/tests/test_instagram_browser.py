import unittest

from automon.integrations.instagram.client_browser import InstagramBrowserClient

c = InstagramBrowserClient(headless=False)


class InstagramClientTest(unittest.TestCase):
    if c.is_running():
        if c.authenticate():
            def test_authenticate(self):
                self.assertTrue(c.is_authenticated())
                c.browser.quit()


if __name__ == '__main__':
    unittest.main()
