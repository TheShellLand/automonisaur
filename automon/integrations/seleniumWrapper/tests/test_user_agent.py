import unittest

from automon.integrations.seleniumWrapper.user_agents import *

test = SeleniumUserAgentBuilder()


class MyTestCase(unittest.TestCase):
    def test_filter(self):
        self.assertFalse(test.filter_agent('xxxxx'))
        self.assertFalse(test.filter_agent('xxxxx', case_sensitive=True))

    def test_pick_random(self):
        self.assertTrue(test.pick_random('xxxxx'))

    def test_most_common_user_agents(self):
        self.assertTrue(public_site_useragents())

    def test_get_bot(self):
        self.assertTrue(test.get_bot())

    def test_get_top(self):
        self.assertTrue(test.get_top())

    def test_get_mobile(self):
        self.assertTrue(test.get_mobile())

    def test_get_mac(self):
        self.assertTrue(test.get_mac())

    def test_get_windows(self):
        self.assertTrue(test.get_windows())

    def test_pick_random_public(self):
        test = SeleniumUserAgentBuilder()
        try:
            self.assertTrue(test.pick_random_public())
        except:
            pass


if __name__ == '__main__':
    unittest.main()
