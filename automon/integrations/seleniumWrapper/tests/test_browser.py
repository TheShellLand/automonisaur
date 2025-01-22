import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    try:
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

            def test_by(self):
                self.assertTrue(browser.by)

            def test_config(self):
                self.assertTrue(browser.config)

            def test_current_url(self):
                if browser.get('http://1.1.1.1'):
                    self.assertTrue(browser._current_url)

            def test_logs(self):
                if browser.get('http://1.1.1.1'):
                    self.assertTrue(browser.logs)

            def test_webdriver(self):
                self.assertTrue(browser.webdriver)

            def test_get_logs(self):
                if browser.get('http://1.1.1.1'):
                    self.assertTrue(browser.get_logs())

            def test_get_log_browser(self):
                if browser.get('http://1.1.1.1'):
                    self.assertTrue(browser.get_log_browser())

            def get_log_driver(self):
                if browser.get('http://1.1.1.1'):
                    self.assertTrue(browser.get_log_driver())

            def get_log_performance(self):
                if browser.get('http://1.1.1.1'):
                    self.assertTrue(browser.get_log_performance())

        browser.quit()

    except:
        pass


if __name__ == '__main__':
    unittest.main()
    browser.quit()
