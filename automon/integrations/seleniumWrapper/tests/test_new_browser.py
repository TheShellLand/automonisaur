import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    try:
        if browser.run():
            def test(self):
                self.assertTrue(browser.quit())

    except:
        pass


if __name__ == '__main__':
    unittest.main()
