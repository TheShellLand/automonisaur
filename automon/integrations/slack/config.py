import os

from automon.log.logger import Logging

log = Logging(name=__name__, level=Logging.ERROR)


class ConfigSlack:
    slack_name = os.getenv('SLACK_USER') or ''
    slack_webhook = os.getenv('SLACK_WEBHOOK') or ''
    slack_proxy = os.getenv('SLACK_PROXY') or ''
    slack_token = os.getenv('SLACK_TOKEN') or ''

    SLACK_DEFAULT_CHANNEL = os.getenv('SLACK_DEFAULT_CHANNEL') or ''
    SLACK_INFO_CHANNEL = os.getenv('SLACK_INFO_CHANNEL') or ''
    SLACK_DEBUG_CHANNEL = os.getenv('SLACK_DEBUG_CHANNEL') or ''
    SLACK_ERROR_CHANNEL = os.getenv('SLACK_ERROR_CHANNEL') or ''
    SLACK_CRITICAL_CHANNEL = os.getenv('SLACK_CRITICAL_CHANNEL') or ''
    SLACK_WARN_CHANNEL = os.getenv('SLACK_WARN_CHANNEL') or ''
    SLACK_TEST_CHANNEL = os.getenv('SLACK_TEST_CHANNEL') or ''

    if not slack_token:
        log.error(f'SLACK_TOKEN not set')

    def __init__(self, slack_name: str = ''):
        self.slack_name = os.getenv('SLACK_USER') or slack_name or ''
