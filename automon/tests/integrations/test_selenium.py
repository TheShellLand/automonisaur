import os
import unittest

from automon.integrations.selenium.browser import SeleniumBrowser as b
from automon.integrations.selenium.config import SeleniumConfig


class SeleniumTest(unittest.TestCase):

    def test_SeleniumConfig(self):
        self.assertTrue(SeleniumConfig())

    def test_SeleniumBrowser(self):
        self.b = b()

        if self.b.connected:
            self.assertFalse(self.b.get('http://555.555.555.555'))

            self.assertTrue(self.b)
            self.assertTrue(self.b.get('http://google.com'))
            self.assertTrue(self.b.get_screenshot_as_png())
            self.assertTrue(self.b.get_screenshot_as_base64())
            self.assertTrue(self.b.save_screenshot())
            self.assertTrue(self.b.save_screenshot(folder='./'))

            self.assertTrue(self.b.close())

    def test_Neo4jSandbox(self):
        self.b = b()

        if self.b.connected:
            actions = [
                self.b.get('https://sandbox.neo4j.com/login'),
                self.b.click('//*[@id="1-email"]', wait=True),
                self.b.type(os.getenv('NEO4J_CLOUD_USER')),
                self.b.type(self.b.Keys.TAB),
                self.b.type(os.getenv('NEO4J_CLOUD_PASSWORD')),
                self.b.type(self.b.Keys.TAB),
                self.b.type(self.b.Keys.TAB),
                self.b.type(self.b.Keys.ENTER),
                self.b.click('//*[@id="project-item-0"]/div[1]/div/div'),
                self.b.click('/html/body/div[5]/div/div[2]/div/div/div[1]/div/div[1]/div[1]/div[2]', wait=True),
                self.b.click('/html/body/div[5]/div/div[2]/div/div/div[2]/div/div/div/button', wait=True),
                # self.b.click('//*[@id="intercom-container"]/div/div/div/div/div[2]/span/svg'),
                # self.b.click('//*[@id="intercom-container"]/div/div/div/div/div[4]/div[2]/button'),
                # self.b.click('//*[@id="intercom-container"]/div/div/div/div/div[2]/span'),
            ]

            [self.assertTrue(x) for x in actions]

            self.assertTrue(self.b.close())


if __name__ == '__main__':
    unittest.main()
