import unittest

from automon.integrations.selenium.browser import SeleniumBrowser
from automon.integrations.selenium.config import SeleniumConfig


class SeleniumTest(unittest.TestCase):
    b = SeleniumBrowser()

    def test_SeleniumConfig(self):
        self.assertTrue(SeleniumConfig())

    def test_SeleniumBrowser(self):

        if self.b.connected:
            self.assertFalse(self.b.get('http://555.555.555.555'))

            self.assertTrue(self.b)
            self.assertTrue(self.b.get('http://google.com'))
            self.assertTrue(self.b.get_screenshot_as_png())
            self.assertTrue(self.b.get_screenshot_as_base64())
            self.assertTrue(self.b.save_screenshot())
            self.assertTrue(self.b.save_screenshot(folder='./'))

            self.assertIsNone(self.b.close())

    def test_Neo4jSandbox(self):
        if self.b.connected:
            self.assertTrue(self.b.get('https://sandbox.neo4j.com/login'))
            self.assertTrue()

            self.assertIsNone(self.b.close())


if __name__ == '__main__':
    unittest.main()
