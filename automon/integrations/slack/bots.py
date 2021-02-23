from slack.web.slack_response import SlackResponse


class BotInfo(SlackResponse):
    def __init__(self, response: dict):
        """{
            "ok": true,
            "bot": {
                "id": "B061F7JD2",
                "deleted": false,
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
        """

        self.status = response.get('ok')
        self.bot = dict(response.get('bot'))
        self.id = self.bot.get('id')
        self.deleted = self.bot.get('deleted')
        self.name = self.bot.get('name')
        self.updated = self.bot.get('updated')
        self.app_id = self.bot.get('app_id')
        self.user_id = self.bot.get('user_id')
        self.icons = self.bot.get('icons')

    def __repr__(self):
        return f'{self.__dict__}'

    def __str__(self):
        return f'{self.__dict__}'

    def __eq__(self, other):
        if not isinstance(other, BotInfo):
            return NotImplemented

        return self.__dict__ == other.__dict__
