import os

from automon.log import Logging

log = Logging(name=__name__, level=Logging.ERROR)


class SlackConfig(object):

    def __init__(self, username=None,
                 webhook=None,
                 proxy=None,
                 token=None,
                 channel=None):
        """Slack config v2
        """

        self.username = username or os.getenv('SLACK_USER') or ''
        self.webhook = webhook or os.getenv('SLACK_WEBHOOK') or ''
        self.proxy = proxy or os.getenv('SLACK_PROXY') or ''
        self.token = token or os.getenv('SLACK_TOKEN') or ''

        self.channel = channel or ''

        self.SLACK_DEFAULT_CHANNEL = os.getenv('SLACK_DEFAULT_CHANNEL') or ''
        self.SLACK_INFO_CHANNEL = os.getenv('SLACK_INFO_CHANNEL') or ''
        self.SLACK_DEBUG_CHANNEL = os.getenv('SLACK_DEBUG_CHANNEL') or ''
        self.SLACK_ERROR_CHANNEL = os.getenv('SLACK_ERROR_CHANNEL') or ''
        self.SLACK_CRITICAL_CHANNEL = os.getenv('SLACK_CRITICAL_CHANNEL') or ''
        self.SLACK_WARN_CHANNEL = os.getenv('SLACK_WARN_CHANNEL') or ''
        self.SLACK_TEST_CHANNEL = os.getenv('SLACK_TEST_CHANNEL') or ''

        if not self.token:
            log.warn(f'missing SLACK_TOKEN')


class ConfigSlack:
    """Slack config v1
    """

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
        log.warn(f'missing SLACK_TOKEN')

    def __init__(self, slack_name: str = ''):
        self.slack_name = os.getenv('SLACK_USER') or slack_name or ''
