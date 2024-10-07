import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    try:
        if browser.run():

            def test_logs(self):

                if browser.get('http://binance.com'):
                    logs = browser.get_log_performance()
                    logs = browser.get_log_browser()
                    logs = browser.get_log_driver()
                    logs = browser.get_logs()

                    browser.quit()

    except:
        pass


if __name__ == '__main__':
    unittest.main()
