import unittest
import asyncio

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper


class Test(unittest.TestCase):
    browser = SeleniumBrowser()
    browser.config.webdriver_wrapper = ChromeWrapper()
    browser.config.webdriver_wrapper.enable_defaults().enable_headless()

    # if asyncio.run(browser.run()):
    asyncio.run(browser.run())

    def test_autosave(self):
        if asyncio.run(self.browser.run()):

            if asyncio.run(self.browser.get('http://bing.com')):
                self.assertTrue(asyncio.run(self.browser.autosave_cookies()))

            asyncio.run(self.browser.quit())


if __name__ == '__main__':
    unittest.main()
