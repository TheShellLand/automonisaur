import unittest


from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper


class Test(unittest.TestCase):
    browser = SeleniumBrowser()
    browser.config.webdriver_wrapper = ChromeWrapper()
    browser.config.webdriver_wrapper.enable_defaults().enable_headless()

    # if browser.run():
    browser.run()

    def test_autosave(self):
        if self.browser.run():

            if self.browser.get('http://bing.com'):
                self.assertTrue(self.browser.autosave_cookies())

            self.browser.quit()


if __name__ == '__main__':
    unittest.main()
