import asyncio
import traceback

from json import dumps
from asyncio import sleep

from automon.helpers.asyncio_ import AsyncStarter
from automon.integrations.slack.client import SlackClient

from automon.integrations.slack.slack_formatting import Emoji, Chat, Format
from automon.log.logger import Logging, INFO, ERROR, WARN, CRITICAL, DEBUG


class AsyncSlackLogging(SlackClient):
    """
    Logging to Slack
    """

    def __init__(self, slack: SlackClient = None, username: str = '', channel: str = '',
                 change_user: bool = False, change_icon: bool = False, debug: bool = True):

        self.slack = slack or SlackClient(username=username, channel=channel)
        self.slack.username = self.slack.username or username
        self.slack.channel = self.slack.channel or channel
        self.slack_username = self.slack.username
        self.slack_channel = self.slack.channel

        # start producer
        self._eventloop = AsyncStarter()
        self.queue = self._eventloop.queue
        self._task = self._eventloop.create_task(self._producer())
        self._stop = False

        # TODO: which takes precedent, icon or url?

        self._icon = Emoji.yay
        self._url = ''
        self.channel = self.slack.SLACK_DEFAULT_CHANNEL or '' \
            if not self.slack_username else f'#{self.slack_username}'
        self._format = Format.blockquote
        self._suffix = ''

        self._warn_icon = Emoji.warning
        self._warn_url = ''
        self.warn_channel = self.slack.SLACK_WARN_CHANNEL or '' \
            if not self.slack_username else f'#{self.slack_username}-warn'
        self._warn_format = Format.blockquote
        self._warn_suffix = ' warn'

        self._info_icon = Emoji.information_source
        self._info_url = ''
        self.info_channel = self.slack.SLACK_INFO_CHANNEL or '' \
            if not self.slack_username else f'#{self.slack_username}-info'
        self._info_format = Format.blockquote
        self._info_suffix = ' info'

        self._debug_icon = Emoji.magnifying_glass
        self._debug_url = ''
        self.debug_channel = self.slack.SLACK_DEBUG_CHANNEL or '' \
            if not self.slack_username else f'#{self.slack_username}-debug'
        self._debug_format = Format.blockquote
        self._debug_suffix = ' debugger'

        self._error_icon = Emoji.sos
        self._error_url = ''
        self.error_channel = self.slack.SLACK_ERROR_CHANNEL or '' \
            if not self.slack_username else f'#{self.slack_username}-error'
        self._error_format = Format.blockquote
        self._error_suffix = ' error'

        self._critical_icon = Emoji.sos
        self._critical_url = ''
        self.critical_channel = self.slack.SLACK_CRITICAL_CHANNEL or '' \
            if not self.slack_username else f'#{self.slack_username}-critical'
        self._critical_format = Format.blockquote
        self._critical_suffix = ' critical'

        self._test_icon = Emoji.yay
        self._test_url = ''
        self.test_channel = self.slack.SLACK_TEST_CHANNEL or '' \
            if not self.slack_username else f'#{self.slack_username}-test'
        self._test_format = Format.blockquote
        self._test_suffix = ' tester'

        if debug:
            self.warn_channel = self.debug_channel
            self.info_channel = self.debug_channel
            self.debug_channel = self.debug_channel
            self.error_channel = self.debug_channel
            self.critical_channel = self.debug_channel
            self.test_channel = self.debug_channel

            self._warn_icon = ''
            self._info_icon = ''
            self._debug_icon = ''
            self._error_icon = ''
            self._critical_icon = ''
            self._test_icon = ''

        if change_user is False:
            self._warn_suffix = ''
            self._info_suffix = ''
            self._debug_suffix = ''
            self._error_suffix = ''
            self._critical_suffix = ''
            self._test_suffix = ''

            self._warn_icon = ''
            self._info_icon = ''
            self._debug_icon = ''
            self._error_icon = ''
            self._critical_icon = ''
            self._test_icon = ''

        if change_icon is False:
            self._warn_icon = ''
            self._info_icon = ''
            self._debug_icon = ''
            self._error_icon = ''
            self._critical_icon = ''
            self._test_icon = ''

        # TODO: can you create an animation out of emojis?

    @staticmethod
    def _msg(msg: object) -> str or None:
        if isinstance(msg, dict):
            return dumps(msg, indent=4)
        if isinstance(msg, list) or isinstance(msg, tuple):
            try:
                new_msg = ''
                for m in msg:
                    new_msg += dumps(m, indent=4)
                return new_msg
            except Exception as _:
                return ''.join(str(msg))
        if msg is None:
            return Chat.none()

        return Chat.string(msg)

    async def _producer(self):
        while True:
            level, channel, text = await self.queue.get()

            if level is WARN:
                await self._warn(channel, text)
            elif level is INFO:
                await self._info(channel, text)
            elif level is DEBUG:
                await self._debug(channel, text)
            elif level is ERROR:
                await self._error(channel, text)
            elif level is CRITICAL:
                await self._critical(channel, text)
            elif level == Logging.TEST:
                await self._test(channel, text)

            if self._stop:
                break

            await sleep(0)

    async def _put_queue(self, level: int, channel: str, msg: str or None):
        await self.queue.put((level, channel, msg))

    def run_until_complete(self):
        while True:
            if self.queue.qsize():
                asyncio.run(sleep(0))
            else:
                break

        self._stop = True
        self.slack._run_until_complete()

    def close(self):
        self.run_until_complete()

    def default(self, msg: str) -> asyncio.tasks:
        asyncio.run(self._put_queue(WARN, self.channel, msg))

    def warn(self, msg: str) -> asyncio.tasks:
        asyncio.run(self._put_queue(WARN, self.warn_channel, msg))

    def info(self, msg: str) -> asyncio.tasks:
        asyncio.run(self._put_queue(INFO, self.info_channel, msg))

    def debug(self, msg: str) -> asyncio.tasks:
        asyncio.run(self._put_queue(DEBUG, self.debug_channel, msg))

    def error(self, msg: str = None) -> asyncio.tasks:
        asyncio.run(self._put_queue(ERROR, self.error_channel, msg))

    def critical(self, msg: str = None) -> asyncio.tasks:
        asyncio.run(self._put_queue(CRITICAL, self.critical_channel, msg))

    def test(self, msg: str or list or dict or tuple) -> asyncio.tasks:
        asyncio.run(self._put_queue(Logging.TEST, self.test_channel, msg))

    async def _warn(self, channel: str, msg: str or list or dict or tuple):
        self.set_slack_config(WARN)
        return await self.slack.chat_postMessage(channel, self._msg(msg))
        # self.set_slack_config()

    async def _info(self, channel: str, msg: str or list or dict or tuple):
        self.set_slack_config(INFO)
        return await self.slack.chat_postMessage(channel, self._msg(msg))

        # self.set_slack_config()

    async def _debug(self, channel: str, msg: str):
        self.set_slack_config(DEBUG)
        return await self.slack.chat_postMessage(channel, Chat.clean(msg))
        # self.set_slack_config()

    async def _error(self, channel: str, msg: str or list or dict or tuple = None,
                     msg_format: Format = None):
        self.set_slack_config(ERROR)

        tb = traceback.format_exc()
        tb = Chat.wrap(tb, Format.codeblock)
        if 'NoneType' not in tb:
            await self.slack.chat_postMessage(channel, tb)

        if msg:
            msg = self._msg(msg)
            if msg_format:
                msg = Chat.Format(msg, msg_format)
            return await self.slack.chat_postMessage(channel, self._msg(msg))
        # self.set_slack_config()

    async def _critical(self, channel: str, msg: str or list or dict or tuple = None):
        self.set_slack_config(CRITICAL)

        tb = traceback.format_exc()
        tb = Chat.wrap(tb, Format.codeblock)
        if 'NoneType' not in tb:
            await self.slack.chat_postMessage(channel, tb)

        if msg:
            msg = self._msg(msg)
            if not isinstance(msg, str):
                msg = Chat.wrap(msg, Format.codeblock)
            return await self.slack.chat_postMessage(channel, msg)
        # self.set_slack_config()

    async def _test(self, channel: str, msg: str):
        self.set_slack_config(Logging.TEST)
        await self.slack.chat_postMessage(channel, self._msg(msg))
        # self.set_slack_config()

    def set_slack_config(self, level=None):

        # TODO: every since moving to asyncio, this isn't used anymore and I don't know how to fix it yet

        if level is WARN:
            self.slack.username = f'{self.slack.username}{self._warn_suffix}'
            self.slack.icon_emoji = self._warn_icon
            self.slack.icon_url = self._warn_url
            self.slack.channel = self.warn_channel

        elif level is INFO:
            self.slack.username = f'{self.slack.username}{self._info_suffix}'
            self.slack.icon_emoji = self._info_icon
            self.slack.icon_url = self._info_url
            self.slack.channel = self.info_channel

        elif level is DEBUG:
            self.slack.username = f'{self.slack.username}{self._debug_suffix}'
            self.slack.icon_emoji = self._debug_icon
            self.slack.icon_url = self._debug_url
            self.slack.channel = self.debug_channel

        elif level is ERROR:
            self.slack.username = f'{self.slack.username}{self._error_suffix}'
            self.slack.icon_emoji = self._error_icon
            self.slack.icon_url = self._error_url
            self.slack.channel = self.error_channel

        elif level is CRITICAL:
            self.slack.username = f'{self.slack.username}{self._critical_suffix}'
            self.slack.icon_emoji = self._critical_icon
            self.slack.icon_url = self._critical_url
            self.slack.channel = self.critical_channel

        elif level == Logging.TEST:
            self.slack.username = f'{self.slack.username}{self._test_suffix}'
            self.slack.icon_emoji = self._test_icon
            self.slack.icon_url = self._test_url
            self.slack.channel = self.test_channel

        elif not level:
            self.slack.username = self.slack_username
            self.slack.channel = self.slack_channel
            self.slack.icon_emoji = ''
            self.slack.icon_url = ''
