import unittest

from automon.integrations.seleniumWrapper.browser import SeleniumBrowser

browser = SeleniumBrowser()
browser.config.set_webdriver().Chrome().enable_defaults().enable_headless()

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0'

browser.config.set_webdriver().webdriver_wrapper.set_user_agent(agent)


class SeleniumClientTest(unittest.TestCase):
    if browser.run():
        def test_user_agent(self):
            self.assertEqual(browser.get_user_agent(), agent)

            browser.quit()


if __name__ == '__main__':
    unittest.main()
