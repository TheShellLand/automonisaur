import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class Test(unittest.TestCase):
    try:
        if browser.run():

            def test_autosave(self):
                if browser.get('http://bing.com'):
                    self.assertTrue(browser.autosave_cookies())

                    browser.quit()

    except:
        pass


if __name__ == '__main__':
    unittest.main()
