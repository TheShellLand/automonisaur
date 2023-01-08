import unittest

from automon.integrations.seleniumWrapper.browser import SeleniumBrowser

browser = SeleniumBrowser()
browser.set_driver(browser.type.chrome_headless)
browser.set_resolution(device_type='web-large')


class SeleniumClientTest(unittest.TestCase):
    if browser.is_running():
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
