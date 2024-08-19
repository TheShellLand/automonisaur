import unittest
import asyncio

from automon.integrations.instagram.client_browser import InstagramBrowserClient

c = InstagramBrowserClient(headless=True)
asyncio.run(c.start())


class InstagramClientTest(unittest.TestCase):

    def test(self):
        if asyncio.run(c.is_ready()):
            asyncio.run(c.browser.get(c.urls.login_page))

        asyncio.run(c.browser.quit())


if __name__ == '__main__':
    unittest.main()
