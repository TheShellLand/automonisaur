import unittest
import asyncio

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults()
browser.config.webdriver_wrapper.enable_headless()


class SeleniumClientTest(unittest.TestCase):

    def test(self):

        if asyncio.run(browser.run()):
            asyncio.run(browser.set_window_size(device_type='web-large'))

            if asyncio.run(browser.get('http://bing.com')):
                self.assertTrue(asyncio.run(browser.save_screenshot()))
                self.assertTrue(asyncio.run(browser.save_screenshot()))
                self.assertTrue(asyncio.run(browser.save_screenshot(folder='./')))

            asyncio.run(browser.quit())


if __name__ == '__main__':
    unittest.main()
