import os
import slack
import random
import asyncio

from slack.web.slack_response import SlackResponse
from slack.errors import SlackApiError

from automon.log.logger import Logging
from automon.helpers.asyncio_ import AsyncStarter
from automon.integrations.slack.config import ConfigSlack

# TODO: maybe separate class for SlackAuth

log = Logging(__name__, level=Logging.ERROR)


class SlackError:
    def __init__(self, error: SlackApiError):
        """The request to the Slack API failed.
        The server responded with:
        {
            "ok": false,
            "error": "missing_scope",
            "needed": "users:read",
            "provided": "chat:write,chat:write.customize,chat:write.public,links:write,links:read,files:read,files:write"
        }
        """

        self._error = error
        self._reason = getattr(self._error, 'reason', '')
        self._response = getattr(self._error, 'response', '')

        if self._reason:
            self.args = getattr(self._reason, 'args', '')
            self.errno = getattr(self._reason, 'errno', '')
            self.reason = getattr(self._reason, 'reason', '')
            self.strerror = getattr(self._reason, 'strerror', '')
            self.verify_code = getattr(self._reason, 'verify_code', '')
            self.verify_message = getattr(self._reason, 'verify_message', '')

        if self._response:
            self.api_url = getattr(self._response, 'api_url' '')

            self.data = dict(getattr(self._response, 'data', ''))
            self.ok = self.data.get('ok', '')
            self.__error = self.data.get('error', '')
            self._needed = self.data.get('needed', '')
            self.provided = self.data.get('provided', '')

            self.headers = getattr(self._response, 'headers', '')
            self.http_verb = getattr(self._response, 'http_verb', '')
            self.req_args = getattr(self._response, 'req_args', '')
            self.status_code = getattr(self._response, 'status_code', '')

    def error(self):
        if self._response:
            return self.__error

        if self._reason:
            return self.strerror

        log.info(f'{NotImplemented}')
        return f'{self._error}'

    def needed(self):
        if self._response:
            return self._needed

        if self._reason:
            return self.strerror

        log.info(f'{NotImplemented}')
        return f'{self._error}'

    def __repr__(self):
        if self._response:
            return f'{self.data}'

        if self._reason:
            return f'{self.strerror}'

        log.info(f'{NotImplemented}')
        return f'{self._error}'

    def __str__(self):
        return self.__repr__()


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


class Slack(ConfigSlack):
    """
    All Slack interactions
    """

    def __init__(self, token: ConfigSlack.slack_token = None, username: str = None,
                 channel: str = None, icon_emoji: str = None, icon_url: str = None):

        self._log = Logging(Slack.__name__, Logging.ERROR)

        self.token = ConfigSlack().slack_token or token

        if not self.token:
            self._log.error(f'Missing SLACK_TOKEN')
            self.client = None
        else:
            self.client = slack.WebClient(token=self.token)

        # TODO: use token to get bot info
        self.username = ConfigSlack().slack_name or username or self._get_bot_info() or ''
        # automonbot-test
        self.channel = ConfigSlack.SLACK_DEFAULT_CHANNEL or channel or ''
        self.icon_emoji = icon_emoji if icon_emoji else ''
        self.icon_url = icon_url if icon_url else ''

        # start consumer
        self._start_loop = AsyncStarter()
        self.queue = self._start_loop.queue
        asyncio.create_task(self._consumer())
        self._stop = False

        # TODO: integrate slacklog
        # self.slacklog = SlackLogging(token)

    def _get_bot_info(self: SlackResponse):
        if self.client:
            try:
                name = BotInfo(self.client.bots_info()).name
                self._log.debug(f'Bot name: {name}')
                return name
            except Exception as e:
                error = SlackError(e)
                self._log.error(
                    f'''{self._get_bot_info.__name__}\tCouldn't get bot name, missing permission: {error.needed}''',
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

        if not self.client:
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

        if not self.client:
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
        while True:
            channel, text = await self.queue.get()

            if self._stop:
                break

            msg = f'{channel} @{self.username}: {text}'

            while True:
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
