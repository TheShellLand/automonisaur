import unittest
import asyncio

from automon.integrations.instagram.client_browser import InstagramBrowserClient

client = InstagramBrowserClient(headless=False)
asyncio.run(client.start())


class InstagramClientTest(unittest.TestCase):

    def test(self):

        if asyncio.run(client.is_ready()):
            asyncio.run(client.browser.get(client.urls.domain))
            if not asyncio.run(client.is_authenticated()):
                asyncio.run(client.authenticate())
        asyncio.run(client.browser.quit())


if __name__ == '__main__':
    unittest.main()
