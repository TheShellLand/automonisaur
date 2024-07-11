import unittest
import asyncio

from automon.integrations.instagram.client_browser import InstagramBrowserClient

c = InstagramBrowserClient(headless=False)
asyncio.run(c.start())


class InstagramClientTest(unittest.TestCase):

    def test(self):

        if asyncio.run(c.is_ready()):
            asyncio.run(c.browser.get(c.urls.domain))
            asyncio.run(c.browser.refresh())
            if asyncio.run(c.authenticate()):
                self.assertTrue(asyncio.run(c.is_authenticated()))
        asyncio.run(c.browser.quit())


if __name__ == '__main__':
    unittest.main()
