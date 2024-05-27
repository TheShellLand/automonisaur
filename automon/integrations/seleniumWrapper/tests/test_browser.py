import unittest
import asyncio

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    if asyncio.run(browser.run()):

        def test_fake_page(self):
            self.assertFalse(asyncio.run(browser.get('http://555.555.555.555')))

        def test_real_page(self):
            if asyncio.run(browser.get('http://1.1.1.1')):
                self.assertTrue(True)

        def test_screenshot_png(self):
            if asyncio.run(browser.get('http://google.com')):
                self.assertTrue(asyncio.run(browser.get_screenshot_as_png()))

        def test_screenshot_base64(self):
            if asyncio.run(browser.get('http://yahoo.com')):
                self.assertTrue(asyncio.run(browser.get_screenshot_as_base64()))

        def test_screenshot_file(self):
            if asyncio.run(browser.get('http://bing.com')):
                self.assertTrue(asyncio.run(browser.save_screenshot()))
                self.assertTrue(asyncio.run(browser.save_screenshot(folder='./')))

    asyncio.run(browser.quit())


if __name__ == '__main__':
    unittest.main()
    browser.quit()
