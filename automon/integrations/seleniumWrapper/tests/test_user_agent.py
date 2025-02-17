import unittest

from automon.integrations.seleniumWrapper.user_agents import *


class MyTestCase(unittest.TestCase):
    def test_filter(self):
        test = SeleniumUserAgentBuilder()
        self.assertFalse(test.filter_agent('xxxxx'))
        self.assertFalse(test.filter_agent('xxxxx', case_sensitive=True))

    def test_random(self):
        test = SeleniumUserAgentBuilder()
        self.assertFalse(test.get_random_agent('xxxxx'))
        self.assertFalse(test.get_random_agent('xxxxx', case_sensitive=True))

    def test_most_common_user_agents(self):
        self.assertTrue(public_site_useragents())

    def test_pick_random_public(self):
        test = SeleniumUserAgentBuilder()
        self.assertTrue(test.pick_random_public())


if __name__ == '__main__':
    unittest.main()
