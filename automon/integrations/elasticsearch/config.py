import os
import warnings

from automon.logger import Logging
from automon.integrations.slack.config import ConfigSlack
from automon.helpers.sanitation import Sanitation

log = Logging('config')


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


class ElasticsearchConfig:

    def __init__(self, proxy=None):
        self.hosts = []
        self.proxy = proxy

        hosts = os.getenv('ELASTICSEARCH_HOSTS')

        if ',' in hosts:
            hosts = hosts.split(',')
        elif ' ' in hosts:
            hosts = hosts.split(' ')

        for host in hosts:
            host = Sanitation.no_spaces(host)
            host = Sanitation.no_quotes(host)
            self.hosts.append(host)
