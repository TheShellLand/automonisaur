import unittest

from automon.integrations.slack.slack import Slack
from automon.integrations.slack.slack_logger import SlackLogging
from automon.integrations.slack.config import ConfigSlack
from automon.integrations.slack.slack_formatting import Format, Chat, Emoji


class SlackTest(unittest.TestCase):
    def test_ConfigSlack(self):
        self.assertTrue(ConfigSlack())

    def test_Slack(self):
        self.assertTrue(Slack())

    def test_SlackLogging(self):
        test = SlackLogging(username='automonbot')

        self.assertTrue(test)
        self.assertIsNone(test.info('info'))
        self.assertIsNone(test.warn('warn'))
        self.assertIsNone(test.debug('debug'))
        self.assertIsNone(test.debug('debug'))
        self.assertIsNone(test.debug('debug'))
        self.assertIsNone(test.error('error'))
        self.assertIsNone(test.critical('critical'))
        self.assertIsNone(test.test({1: 2}))
        self.assertIsNone(test.test((1, 2)))
        self.assertIsNone(test.test('test'))
        self.assertIsNone(test.test(None))
        self.assertIsNone(test.close())

    def test_Format(self):
        self.assertTrue(Format.blockquote)
        self.assertTrue(Format.codeblock)

    def test_Chat(self):
        self.assertTrue(Chat.Format('test', Format.codeblock))
        self.assertTrue(Chat.wrap('test', Format.blockquote))
        self.assertFalse(Chat.none())
        self.assertTrue(Chat.clean('test'))
        self.assertFalse(Chat.clean(None))
        self.assertTrue(Chat.string('test'))
        self.assertFalse(Chat.string(None))
        self.assertFalse(Chat.multi_to_single_line(None))
        self.assertFalse(Chat.multi_to_single_line('\n'))
        self.assertTrue(Chat.multi_to_single_line('test'))
        self.assertTrue(Chat.multi_to_single_line('test\n'))
        self.assertTrue(Chat.multi_to_single_line('test\ntest'))


# if __name__ == '__main__':
#     unittest.main()
