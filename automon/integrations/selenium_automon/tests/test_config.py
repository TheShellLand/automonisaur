import unittest

from automon.integrations.selenium_automon.config import SeleniumConfig


class SeleniumConfigTest(unittest.TestCase):
    def test_config(self):
        self.assertTrue(SeleniumConfig())


if __name__ == '__main__':
    unittest.main()
