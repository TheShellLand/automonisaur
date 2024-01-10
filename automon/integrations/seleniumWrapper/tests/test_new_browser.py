import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults()
browser.config.webdriver_wrapper.enable_headless()


class SeleniumClientTest(unittest.TestCase):
    if browser.run():
        async def test(self):
            await browser.quit()


if __name__ == '__main__':
    unittest.main()
