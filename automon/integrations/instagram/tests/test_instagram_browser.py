import unittest

from automon.integrations.instagram.client_browser import InstagramBrowserClient


class InstagramClientTest(unittest.TestCase):
    c = InstagramBrowserClient(headless=True)
    c.browser.run()

    if c.is_running():
        c.browser.get(c.urls.login_page)

        # user
        login_user = c.browser.wait_for_xpath(c.xpaths.login_user)
        c.browser.action_click(login_user, 'user')
        c.browser.action_type(c.login)

        # password
        password = c.browser.wait_for_xpath(c.xpaths.login_pass)
        c.browser.action_click(password, 'password')

        c.browser.quit()


if __name__ == '__main__':
    unittest.main()
