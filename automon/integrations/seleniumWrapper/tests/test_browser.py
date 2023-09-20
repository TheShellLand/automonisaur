import unittest

from automon.integrations.seleniumWrapper.browser import SeleniumBrowser

browser = SeleniumBrowser()
browser.config.set_webdriver.Chrome().enable_defaults()


class SeleniumClientTest(unittest.TestCase):
    if browser.run():
        def test(self):
            self.assertFalse(browser.get('http://555.555.555.555'))
            if browser.get('http://1.1.1.1'):
                self.assertTrue(True)

            if browser.get('http://google.com'):
                self.assertTrue(browser.get_screenshot_as_png())

            if browser.get('http://yahoo.com'):
                self.assertTrue(browser.get_screenshot_as_base64())

            if browser.get('http://bing.com'):
                self.assertTrue(browser.save_screenshot())
                self.assertTrue(browser.save_screenshot(folder='./'))

            browser.quit()


if __name__ == '__main__':
    unittest.main()
