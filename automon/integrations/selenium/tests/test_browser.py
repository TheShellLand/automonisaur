import unittest

from automon.integrations.selenium.browser import SeleniumBrowser

browser = SeleniumBrowser()
browser.set_browser(browser.type.chrome)


class SeleniumClientTest(unittest.TestCase):
    if browser.isRunning():
        def test_get(self):
            self.assertFalse(browser.get('http://555.555.555.555'))
            if browser.get('http://1.1.1.1'):
                self.assertTrue(True)

        def test_get_screenshot_as_png(self):
            self.assertTrue(browser.get_screenshot_as_png())

        def test_get_screenshot_as_base64(self):
            self.assertTrue(browser.get_screenshot_as_base64())

        def test_save_screenshot(self):
            self.assertTrue(browser.save_screenshot())
            self.assertTrue(browser.save_screenshot(folder='./'))


if __name__ == '__main__':
    unittest.main()
