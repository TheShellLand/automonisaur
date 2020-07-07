import os
import slack
import random
import asyncio

from automon.config import ConfigSlack
from automon.logger import Logging
from automon.helpers.asyncio_ import AsyncStarter

# TODO: maybe separate class for SlackAuth

log = Logging('slack', level=Logging.INFO)


class Slack(ConfigSlack):
    """
    All Slack interactions
    """

    def __init__(self, token: ConfigSlack.slack_token = None, username: str = None,
                 channel: str = None, icon_emoji: str = None, icon_url: str = None):

        self.token = token if token else ConfigSlack.slack_token

        if not self.token:
            log.error(f'slack is called, but SLACK_TOKEN is not set')
            self.client = None
        else:
            self.client = slack.WebClient(token=self.token)

        self.username = username if username else ''
        # automonbot-test
        self.channel = channel if channel else ''
        self.icon_emoji = icon_emoji if icon_emoji else ''
        self.icon_url = icon_url if icon_url else ''

        # start consumer
        self._start_loop = AsyncStarter()
        self.queue = self._start_loop.queue
        asyncio.create_task(self._consumer())

        # TODO: integrate slacklog
        # self.slacklog = SlackLogging(token)

    async def _consumer(self):

        burst = 0
        burst_max = 0
        retry = 0
        while True:
            channel, text = await self.queue.get()

            msg = f'{channel} @{self.username}: {text}'

            if text is None:
                break

            while True:
                try:
                    log.debug(msg)
                    response = self.client.chat_postMessage(
                        text=text, channel=channel, username=self.username,
                        icon_emoji=self.icon_emoji, icon_url=self.icon_url)
                    assert response["ok"]

                    if not retry and self.queue.qsize() > 10:
                        # if a lot in the queue, try bursting
                        await asyncio.sleep(random.choice(range(2)))
                    else:
                        log.info(f'sleeping, queue size is {self.queue.qsize()}')
                        await asyncio.sleep(random.choice(range(4)))

                    log.info(f'Burst: {burst}, Retry: {retry}, Queue {self.queue.qsize()}')

                    burst += 1
                    retry = 0

                    break
                except Exception as e:
                    retry += 1
                    burst_max = burst
                    log.error(f'Burst max: {burst_max}, Retry: {retry}', enable_traceback=False)
                    burst = 0
                    # log.error(e)

    def _run_until_complete(self):
        while True:
            if self.queue.qsize():
                asyncio.run(asyncio.sleep(0))
            else:
                break

    async def chat_postMessage(self, channel: str, text: str) -> slack.WebClient.chat_postMessage:

        if not self.client:
            return False

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

        if not self.client:
            return False

        # check if file exists
        if not os.path.isfile(file):
            log.error(f'File not found: {file}')
            log.error(f'Working dir: {os.getcwd()}')
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

        log.debug(f'File uploaded: {file} ({file_size}B) ({self.username}')

        return response
