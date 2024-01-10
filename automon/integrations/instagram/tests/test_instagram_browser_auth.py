import unittest
import asyncio

from automon.integrations.instagram.client_browser import InstagramBrowserClient

c = InstagramBrowserClient(headless=True)
asyncio.run(c.start())


class InstagramClientTest(unittest.TestCase):

    async def test(self):

        if c.is_running():
            await c.browser.get(c.urls.domain)
            await c.browser.add_cookie_from_base64()
            await c.browser.refresh()
            if await c.is_authenticated():
                self.assertTrue(await c.is_authenticated())
                await c.browser.quit()


if __name__ == '__main__':
    unittest.main()
