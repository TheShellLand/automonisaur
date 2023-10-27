import unittest

from automon.integrations.seleniumWrapper.browser import SeleniumBrowser

browser = SeleniumBrowser()
browser.config.set_webdriver().Chrome().enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    if browser.run():
        def test(self):
            browser.quit()


if __name__ == '__main__':
    unittest.main()
