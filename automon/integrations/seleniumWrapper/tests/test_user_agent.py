import unittest

from automon.integrations.seleniumWrapper.user_agents import *


class MyTestCase(unittest.TestCase):
    def test_filter(self):
        test = SeleniumUserAgentBuilder()
        self.assertTrue(test.filter_agent('applewebkit'))
        self.assertTrue(test.filter_agent('AppleWebKit', case_sensitive=True))

        self.assertFalse(test.filter_agent('xxxxx'))
        self.assertFalse(test.filter_agent('xxxxx', case_sensitive=True))

    def test_random(self):
        test = SeleniumUserAgentBuilder()
        self.assertTrue(test.get_random_agent('applewebkit'))
        self.assertTrue(test.get_random_agent('AppleWebKit', case_sensitive=True))

        self.assertFalse(test.get_random_agent('xxxxx'))
        self.assertFalse(test.get_random_agent('xxxxx', case_sensitive=True))

    def test_most_common_user_agents(self):
        self.assertIsNotNone(site_useragents())


if __name__ == '__main__':
    unittest.main()
