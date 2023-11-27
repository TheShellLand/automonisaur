import unittest

from automon.integrations.seleniumWrapper.browser import SeleniumBrowser
from automon.integrations.seleniumWrapper.config_webdriver_chrome import ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    if browser.run():
        def test(self):
            browser.quit()


if __name__ == '__main__':
    unittest.main()
