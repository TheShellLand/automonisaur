import unittest

from automon.integrations.instagram.client_browser import InstagramBrowserClient

c = InstagramBrowserClient(headless=False)


class InstagramClientTest(unittest.TestCase):
    if c.is_running():
        c.browser.get(c.urls.login_page)

        # user
        login_user = c.browser.wait_for_xpath(c.xpaths.login_user)
        c.browser.action_click(login_user, 'user')
        c.browser.action_type(c.login)

        c.browser.quit()


if __name__ == '__main__':
    unittest.main()
