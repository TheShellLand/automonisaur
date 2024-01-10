import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults()
browser.config.webdriver_wrapper.enable_headless()


class SeleniumClientTest(unittest.TestCase):

    async def test(self):
        if browser.run():
            await browser.set_window_size(device_type='web-large')
            while True:

                try:
                    if await browser.get('http://bing.com'):
                        self.assertTrue(await browser.save_screenshot())
                        self.assertTrue(await browser.save_screenshot())
                        self.assertTrue(await browser.save_screenshot(folder='./'))

                    await browser.quit()
                    break

                except:
                    pass


if __name__ == '__main__':
    unittest.main()
