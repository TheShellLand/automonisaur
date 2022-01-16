import unittest

from automon.integrations.slack.client import SlackClient, SlackError, BotInfo
from automon.integrations.slack.slack_logger import AsyncSlackLogging
from automon.integrations.slack.config import ConfigSlack
from automon.integrations.slack.slack_formatting import Format, Chat, Emoji


class SlackTest(unittest.TestCase):

    def test_SlackLogging(self):
        test = AsyncSlackLogging(username='automonbot')

        self.assertTrue(test)
        self.assertIsNone(test.info('info'))
        self.assertIsNone(test.warn('warn'))
        self.assertIsNone(test.debug('debug'))
        self.assertIsNone(test.error('error'))
        self.assertIsNone(test.critical('critical'))
        self.assertIsNone(test.test('test'))
        self.assertIsNone(test.close())


if __name__ == '__main__':
    unittest.main()
