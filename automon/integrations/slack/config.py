import os

from automon.log.logger import Logging

log = Logging(__name__)


class ConfigSlack:
    slack_webhook = os.getenv('SLACK_WEBHOOK')
    slack_proxy = os.getenv('SLACK_PROXY')
    slack_token = os.getenv('SLACK_TOKEN')

    SLACK_DEFAULT_CHANNEL = os.getenv('SLACK_DEFAULT_CHANNEL') or ''
    SLACK_INFO_CHANNEL = os.getenv('SLACK_INFO_CHANNEL') or ''
    SLACK_DEBUG_CHANNEL = os.getenv('SLACK_DEBUG_CHANNEL') or ''
    SLACK_ERROR_CHANNEL = os.getenv('SLACK_ERROR_CHANNEL') or ''
    SLACK_CRITICAL_CHANNEL = os.getenv('SLACK_CRITICAL_CHANNEL') or ''
    SLACK_WARN_CHANNEL = os.getenv('SLACK_WARN_CHANNEL') or ''
    SLACK_TEST_CHANNEL = os.getenv('SLACK_TEST_CHANNEL') or ''

    if not slack_token:
        log.debug(f'SLACK_TOKEN not set')

    def __init__(self, slack_name: str = ''):
        self.slack_name = os.getenv('SLACK_USER') or slack_name or ''
        self.slack_webhook = os.getenv('SLACK_WEBHOOK')
        self.slack_proxy = os.getenv('SLACK_PROXY')
        self.slack_token = os.getenv('SLACK_TOKEN')

        self.SLACK_DEFAULT_CHANNEL = os.getenv('SLACK_DEFAULT_CHANNEL') or ''
        self.SLACK_INFO_CHANNEL = os.getenv('SLACK_INFO_CHANNEL') or ''
        self.SLACK_DEBUG_CHANNEL = os.getenv('SLACK_DEBUG_CHANNEL') or ''
        self.SLACK_ERROR_CHANNEL = os.getenv('SLACK_ERROR_CHANNEL') or ''
        self.SLACK_CRITICAL_CHANNEL = os.getenv('SLACK_CRITICAL_CHANNEL') or ''
        self.SLACK_WARN_CHANNEL = os.getenv('SLACK_WARN_CHANNEL') or ''
        self.SLACK_TEST_CHANNEL = os.getenv('SLACK_TEST_CHANNEL') or ''
