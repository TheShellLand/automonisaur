import unittest

from automon.integrations.seleniumWrapper.browser import SeleniumBrowser

browser = SeleniumBrowser()

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0'
opts = [f"user-agent={agent}"]

browser.set_driver(browser.type.chrome(options=opts))


class SeleniumClientTest(unittest.TestCase):
    if browser.is_running():
        def test_user_agent(self):
            self.assertEqual(browser.get_user_agent(), agent)

            browser.quit()


if __name__ == '__main__':
    unittest.main()
