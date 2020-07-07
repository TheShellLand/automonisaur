import os
import warnings
import slack

from automon.logger import Logging

log = Logging('config')


class ConfigSlack:
    slack_webhook = os.getenv('SLACK_WEBHOOK')
    slack_proxy = os.getenv('SLACK_PROXY')
    slack_token = os.getenv('SLACK_TOKEN')

    if not slack_token:
        log.debug(f'SLACK_TOKEN not set')

    def __init__(self, slack_name='Automon Slack bot'):
        self.slack = slack
        self.slack_name = slack_name
        self.slack_webhook = os.getenv('SLACK_WEBHOOK')
        self.slack_proxy = os.getenv('SLACK_PROXY')
        self.slack_token = os.getenv('SLACK_TOKEN')


class ConfigES:
    elasticsearch_endpoint = os.getenv('ELASTICSEARCH_ENDPOINT')

    def __init__(self):
        if not self.elasticsearch_endpoint:
            raise Exception('elasticsearch endpoint missing: {}'.format(self.elasticsearch_endpoint))


class ConfigESSnapshotBot:
    def __init__(self):
        self.slack = ConfigSlack(slack_name='Elasticsearch JVM Monitor bot')
        self.slack_name = 'Elasticsearch Elasticsearch Daily Monitor bot'
        warnings.warn('self.slack_name is depreciated, use self.slack.slack_name instead', DeprecationWarning)
        self.slack_webhook = ConfigSlack.slack_webhook
        warnings.warn('self.slack_webhook is depreciated, use self.slack.slack_webhook instead', DeprecationWarning)
        self.slack_proxy = ConfigSlack.slack_proxy
        warnings.warn('self.slack_proxy is depreciated, use self.slack.slack_proxy instead', DeprecationWarning)
        self.elasticsearch_endpoint = ConfigES.elasticsearch_endpoint
        self.elasticsearch_repository = os.getenv('ELASTICSEARCH_REPOSITORY')
        self.snapshots_prefix = os.getenv('SNAPSHOTS_PREFIX')


class ConfigESJVMBot:
    def __init__(self):
        self.slack = ConfigSlack(slack_name='Elasticsearch JVM Monitor bot')
        self.slack_name = 'Elasticsearch JVM Monitor bot'
        warnings.warn('self.slack_name is depreciated, use self.slack.slack_name instead', DeprecationWarning)
        self.slack_webhook = ConfigSlack.slack_webhook
        warnings.warn('self.slack_webhook is depreciated, use self.slack.slack_webhook instead', DeprecationWarning)
        self.slack_proxy = ConfigSlack.slack_proxy
        warnings.warn('self.slack_proxy is depreciated, use self.slack.slack_proxy instead', DeprecationWarning)
        self.elasticsearch_endpoint = ConfigES.elasticsearch_endpoint
