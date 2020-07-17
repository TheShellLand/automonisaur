import os

from automon.log.logger import Logging

log = Logging(__name__)


class ConfigSlack:
    slack_webhook = os.getenv('SLACK_WEBHOOK')
    slack_proxy = os.getenv('SLACK_PROXY')
    slack_token = os.getenv('SLACK_TOKEN')

    if not slack_token:
        log.debug(f'SLACK_TOKEN not set')

    def __init__(self, slack_name: str = None):
        self.slack_name = slack_name if slack_name else ''
        self.slack_webhook = os.getenv('SLACK_WEBHOOK')
        self.slack_proxy = os.getenv('SLACK_PROXY')
        self.slack_token = os.getenv('SLACK_TOKEN')
