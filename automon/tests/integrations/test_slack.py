import unittest

from automon.integrations.slack.client import SlackClient
from automon.integrations.slack.error import SlackError
from automon.integrations.slack.bots import BotInfo
from automon.integrations.slack.config import SlackConfig
from automon.integrations.slack.slack_formatting import Format, Chat, Emoji


class ConfigTest(unittest.TestCase):
    def test_SlackConfig(self):
        self.assertTrue(SlackConfig())


class ClientTest(unittest.TestCase):

    def test_Slack(self):
        self.assertTrue(SlackClient())

    def test_SlackError(self):
        self.assertTrue(SlackError)

    def test_Format(self):
        self.assertTrue(Format.blockquote)
        self.assertTrue(Format.codeblock)


class BotTest(unittest.TestCase):
    def test_BotInfo(self):
        bot = {
            "ok": True,
            "bot": {
                "id": "B061F7JD2",
                "deleted": False,
                "name": "beforebot",
                "updated": 1449272004,
                "app_id": "A161CLERW",
                "user_id": "U012ABCDEF",
                "icons": {
                    "image_36": "https://...",
                    "image_48": "https://...",
                    "image_72": "https://..."
                }
            }
        }

        self.assertTrue(BotInfo)
        self.assertTrue(BotInfo(bot))
        self.assertEqual(BotInfo(bot), BotInfo(bot))
        self.assertNotEqual(BotInfo(bot), bot)
        self.assertTrue(f'{BotInfo(bot)}')


class FormatTest(unittest.TestCase):

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

    def test_Emoji(self):
        self.assertTrue(Emoji.warning)
        self.assertTrue(Emoji.information_source)
        self.assertTrue(Emoji.magnifying_glass)
        self.assertTrue(Emoji.sos)
        self.assertTrue(Emoji.waiting)
        self.assertTrue(Emoji.still_waiting)
        self.assertTrue(Emoji.grey_question)
        self.assertTrue(Emoji.questionbang)
        self.assertTrue(Emoji.skull)
        self.assertTrue(Emoji.skull_and_crossbones)
        self.assertTrue(Emoji.file)
        self.assertTrue(Emoji.announcement)
        self.assertTrue(Emoji.yay)


if __name__ == '__main__':
    unittest.main()
