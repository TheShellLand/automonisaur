import unittest

from automon.integrations.instagram.client_browser import InstagramBrowserClient


class InstagramClientTest(unittest.TestCase):
    c = InstagramBrowserClient(headless=True)
    c.browser.run()

    if c.is_running():
        c.browser.get(c.urls.domain)
        c.browser.add_cookie_from_base64()
        c.browser.refresh()
        if c.is_authenticated():
            def test_authenticate(self):
                self.assertTrue(self.c.is_authenticated())
                self.c.browser.quit()


if __name__ == '__main__':
    unittest.main()
