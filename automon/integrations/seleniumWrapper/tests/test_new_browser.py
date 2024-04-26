import unittest
import asyncio

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults()
browser.config.webdriver_wrapper.enable_headless()


class SeleniumClientTest(unittest.TestCase):
    if asyncio.run(browser.run()):
        def test(self):
            self.assertTrue(asyncio.run(browser.quit()))


if __name__ == '__main__':
    unittest.main()
