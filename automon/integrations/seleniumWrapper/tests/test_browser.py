import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults()
browser.config.webdriver_wrapper.enable_headless()


class SeleniumClientTest(unittest.TestCase):
    async def test_fake_page(self):
        if await browser.run():
            self.assertFalse(browser.get('http://555.555.555.555'))

    async def test_real_page(self):
        if await browser.run():
            if await browser.get('http://1.1.1.1'):
                self.assertTrue(True)

    async def test_screenshot_png(self):
        if await browser.run():
            if await browser.get('http://google.com'):
                self.assertTrue(await browser.get_screenshot_as_png())

    async def test_screenshot_base64(self):
        if await browser.run():
            if await browser.get('http://yahoo.com'):
                self.assertTrue(await browser.get_screenshot_as_base64())

    async def test_screenshot_file(self):
        if await browser.run():
            if await browser.get('http://bing.com'):
                self.assertTrue(await browser.save_screenshot())
                self.assertTrue(await browser.save_screenshot(folder='./'))


if __name__ == '__main__':
    unittest.main()
    browser.quit()
