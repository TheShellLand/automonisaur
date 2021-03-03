import unittest

from automon.integrations.selenium.browser import SeleniumBrowser
from automon.integrations.selenium.config import SeleniumConfig


class SeleniumTest(unittest.TestCase):
    def test_SeleniumConfig(self):
        self.assertTrue(SeleniumConfig())

    def test_SeleniumBrowser(self):
        b = SeleniumBrowser()

        if b.connected:
            self.assertTrue(b)
            self.assertFalse(b.get('http://555.555.555.555'))
            self.assertTrue(b.get('http://google.com'))
            self.assertTrue(b.get_screenshot_as_png())
            self.assertTrue(b.get_screenshot_as_base64())
            self.assertTrue(b.save_screenshot())
            self.assertTrue(b.save_screenshot(folder='./'))


if __name__ == '__main__':
    unittest.main()
