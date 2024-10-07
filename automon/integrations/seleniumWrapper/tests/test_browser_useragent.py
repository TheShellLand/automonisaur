import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0'

browser.config.webdriver_wrapper.set_user_agent(agent)


class SeleniumClientTest(unittest.TestCase):
    try:
        if browser.run():
            def test_user_agent(self):
                self.assertEqual(browser.user_agent, agent)

                browser.quit()
    except:
        pass


if __name__ == '__main__':
    unittest.main()
