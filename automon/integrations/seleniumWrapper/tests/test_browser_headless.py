import unittest

from automon.integrations.seleniumWrapper.browser import SeleniumBrowser

browser = SeleniumBrowser()
browser.config.set_webdriver().Chrome().enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    if browser.run():
        browser.set_window_size(device_type='web-large')

        def test(self):
            while True:

                try:
                    if browser.get('http://bing.com'):
                        self.assertTrue(browser.save_screenshot())
                        self.assertTrue(browser.save_screenshot())
                        self.assertTrue(browser.save_screenshot(folder='./'))

                    browser.quit()
                    break

                except:
                    pass


if __name__ == '__main__':
    unittest.main()
