import unittest

from automon.integrations.seleniumWrapper.browser import SeleniumBrowser
from automon.integrations.seleniumWrapper.config_webdriver_chrome import ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    if browser.run():
        def test_fake_page(self):
            self.assertFalse(browser.get('http://555.555.555.555'))

        def test_real_page(self):
            if browser.get('http://1.1.1.1'):
                self.assertTrue(True)

        def test_screenshot_png(self):
            if browser.get('http://google.com'):
                self.assertTrue(browser.get_screenshot_as_png())

        def test_screenshot_base64(self):
            if browser.get('http://yahoo.com'):
                self.assertTrue(browser.get_screenshot_as_base64())

        def test_screenshot_file(self):
            if browser.get('http://bing.com'):
                self.assertTrue(browser.save_screenshot())
                self.assertTrue(browser.save_screenshot(folder='./'))


if __name__ == '__main__':
    unittest.main()
    browser.quit()
