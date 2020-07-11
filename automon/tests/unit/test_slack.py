import unittest

from automon.integrations.slack.slack import Slack
from automon.integrations.slack.config import ConfigSlack


class SlackTest(unittest.TestCase):
    def test_ConfigSlack(self):
        self.assertTrue(ConfigSlack())

    def test_Slack(self):
        self.assertTrue(Slack())

# if __name__ == '__main__':
#     unittest.main()
