import unittest
import asyncio

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    if asyncio.run(browser.run()):

        def test_logs(self):

            if asyncio.run(browser.get('http://binance.com')):
                logs = asyncio.run(browser.get_log_performance())
                logs = asyncio.run(browser.get_log_browser())
                logs = asyncio.run(browser.get_log_driver())
                logs = asyncio.run(browser.get_logs())

                pass

            asyncio.run(browser.quit())


if __name__ == '__main__':
    unittest.main()
