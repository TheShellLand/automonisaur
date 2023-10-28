import unittest

from automon.integrations.instagram.client_browser import InstagramBrowserClient


class InstagramClientTest(unittest.TestCase):
    c = InstagramBrowserClient(headless=False)
    c.browser.run()

    if c.is_running():
        if c.authenticate():
            def test_authenticate(self):
                self.assertTrue(self.c.is_authenticated())
                self.c.browser.quit()


if __name__ == '__main__':
    unittest.main()
