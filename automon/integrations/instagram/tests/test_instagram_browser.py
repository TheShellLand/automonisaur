import unittest

from automon.integrations.instagram.client_browser import InstagramBrowserClient

c = InstagramBrowserClient(headless=True)
c.start()


class InstagramClientTest(unittest.TestCase):

    def test(self):
        if c.is_ready():
            c.browser.get(c.urls.login_page)

        c.browser.quit()


if __name__ == '__main__':
    unittest.main()
