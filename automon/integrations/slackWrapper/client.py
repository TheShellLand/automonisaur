import os
import slack

from automon.log import Logging

from .config import SlackConfig
from .bots import BotInfo
from .error import SlackError


class SlackClient(SlackConfig):

    def __init__(self, token: str = None,
                 config: SlackConfig = None,
                 username: str = None,
                 channel: str = None,
                 icon_emoji: str = None,
                 icon_url: str = None):
        """Slack client
        """

        self._log = Logging(SlackClient.__name__, Logging.ERROR)

        self.config = config or SlackConfig(token=token, username=username, channel=channel)
        self.client = slack.WebClient(token=self.config.token)

        try:
            self.connected = True if self.client.auth_test() else False
        except:
            self.connected = False

        # TODO: use token to get bot info
        self.username = self.config.username or self._get_bot_info() or ''
        self.channel = self.config.SLACK_DEFAULT_CHANNEL
        self.icon_emoji = icon_emoji or ''
        self.icon_url = icon_url or ''

        self.queue = None

    def _get_bot_info(self):
        if not self.connected:
            return False

        try:
            name = BotInfo(self.client.bots_info()).name
            self._log.debug(f'Bot name: {name}')
            return name
        except Exception as e:
            error = SlackError(e)
            self._log.error(
                f'''[{self._get_bot_info.__name__}]\tCouldn't get bot name, missing permission: {error.needed}''',
                enable_traceback=False)
            return ''

        return ''

    def chat_postMessage(self, channel: str, text: str) -> slack.WebClient.chat_postMessage:

        if self.connected:
            return False

        if not text:
            return SyntaxError

        msg = f'{channel} @{self.username}: {text}'
        self._log.debug(msg)

        try:
            response = self.client.chat_postMessage(
                text=text, channel=channel, username=self.username,
                icon_emoji=self.icon_emoji, icon_url=self.icon_url)
            assert response["ok"]
            return response
        except Exception as e:
            self._log.error(e, enable_traceback=False)

        return False

    def files_upload(self, file, filename=None):
        """
        Upload file to slack

        note: username does nothing
        note: icon_emoji does nothing
        note: title takes precedent over filename
        note: title will display full string
        note: filename displays only filename, no extension

        :param file: path to file
        :param filename: (Optional) filename
        :return: Slack response or False
        """

        if not self.connected:
            return False

        # check if file exists
        if not os.path.isfile(file):
            self._log.error(f'File not found: {file}')
            self._log.error(f'Working dir: {os.getcwd()}')
            return False

        # get filename
        if not filename:
            filename = os.path.split(file)

        # get file size
        file_size = os.path.getsize(file)

        title = f'{filename} ({file_size}B'

        # TODO: add string validation for `filename`
        # TODO: find a way to change username for files_upload

        response = self.client.files_upload(
            file=file, filename=filename, title=title, username=self.username, channels=self.channel)

        assert response["ok"]
        self._log.debug(f'File uploaded: {file} ({file_size}B) ({self.username}')

        return response
