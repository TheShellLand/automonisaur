import unittest
import asyncio

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    if asyncio.run(browser.run()):

        def test(self):

            if asyncio.run(browser.get('http://1.1.1.1')):

                if asyncio.run(browser.check_page_load_finished()):
                    self.assertTrue(asyncio.run(browser.save_screenshot()))
                    self.assertTrue(asyncio.run(browser.save_screenshot(folder='./')))

            asyncio.run(browser.quit())


if __name__ == '__main__':
    unittest.main()
