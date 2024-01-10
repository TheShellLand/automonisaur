import unittest
import asyncio

from automon.integrations.instagram.client_browser import InstagramBrowserClient

c = InstagramBrowserClient(headless=True)
asyncio.run(c.start())


class InstagramClientTest(unittest.TestCase):

    async def test(self):
        if await c.is_running():
            await c.browser.get(c.urls.login_page)

            # user
            login_user = await c.browser.wait_for_xpath(c.xpaths.login_user)
            await c.browser.action_click(login_user, 'user')
            await c.browser.action_type(c.login)

            # password
            password = await c.browser.wait_for_xpath(c.xpaths.login_pass)
            await c.browser.action_click(password, 'password')

            await c.browser.quit()


if __name__ == '__main__':
    unittest.main()
