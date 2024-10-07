import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    try:
        if browser.run():

            def test(self):

                if browser.get('http://1.1.1.1'):

                    if browser.check_page_load_finished():
                        self.assertTrue(browser.save_screenshot())
                        self.assertTrue(browser.save_screenshot(folder='./'))

                        browser.quit()

    except:
        pass


if __name__ == '__main__':
    unittest.main()
