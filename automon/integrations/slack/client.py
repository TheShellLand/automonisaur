import os
import slack
import random
import asyncio

from automon.log.logger import Logging
from automon.helpers.asyncio_ import AsyncStarter
from automon.integrations.slack.bots import BotInfo
from automon.integrations.slack.error import SlackError
from automon.integrations.slack.config import ConfigSlack


class SlackClient(ConfigSlack):
    """
    All Slack interactions
    """

    def __init__(self, token: str = ConfigSlack.slack_token, username: str = '',
                 channel: str = '', icon_emoji: str = None, icon_url: str = None):

        self._log = Logging(SlackClient.__name__, Logging.ERROR)

        self.token = ConfigSlack.slack_token or token
        self.client = slack.WebClient(token=token)

        try:
            self.connected = True if self.client.auth_test() else False
        except:
            self.connected = False

        # TODO: use token to get bot info
        self.username = ConfigSlack.slack_name or username or self._get_bot_info() or ''
        self.channel = ConfigSlack.SLACK_DEFAULT_CHANNEL or channel or ''
        self.icon_emoji = icon_emoji or ''
        self.icon_url = icon_url or ''

        # start consumer
        self._eventloop = AsyncStarter()
        self.queue = self._eventloop.queue
        self.task = self._eventloop.create_task(self._consumer())
        self._stop = False

        # TODO: integrate slacklog
        # self.slacklog = SlackLogging(token)

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

    def _run_until_complete(self):
        while True:
            if self.queue.qsize():
                asyncio.run(asyncio.sleep(0))
            else:
                break
        self._stop = True

    async def chat_postMessage(self, channel: str, text: str) -> slack.WebClient.chat_postMessage:

        if not self.connected:
            return False

        if not text:
            return SyntaxError

        await self.queue.put((channel, text))

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

    async def _consumer(self):

        burst = 0
        burst_max = 0
        retry = 0
        while self.connected:
            channel, text = await self.queue.get()

            if self._stop:
                break

            msg = f'{channel} @{self.username}: {text}'

            while self.connected:
                try:
                    self._log.debug(msg)
                    response = self.client.chat_postMessage(
                        text=text, channel=channel, username=self.username,
                        icon_emoji=self.icon_emoji, icon_url=self.icon_url)
                    assert response["ok"]

                    if not retry and self.queue.qsize() > 10:
                        # if a lot in the queue, try bursting
                        await asyncio.sleep(random.choice(range(2)))
                    else:
                        sleep = random.choice(range(4))
                        self._log.debug(f'sleeping {sleep}, queue size is {self.queue.qsize()}')
                        await asyncio.sleep(sleep)

                    self._log.debug(f'Burst: {burst}, Retry: {retry}, Queue {self.queue.qsize()}')

                    burst += 1
                    retry = 0

                    break
                except Exception as e:
                    if retry > 5:
                        break

                    retry += 1
                    burst_max = burst
                    error = SlackError(e)
                    self._log.error(
                        f'{self._consumer.__name__}\t{error.error}\t{msg}\tRetry: {retry}, Burst max: {burst_max}',
                        enable_traceback=False)
                    burst = 0
