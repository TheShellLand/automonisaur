import os
import warnings

from automon.logger import Logging
from automon.helpers.sanitation import Sanitation

log = Logging('config')


class ConfigES:
    elasticsearch_endpoint = os.getenv('ELASTICSEARCH_ENDPOINT') or os.getenv('ELASTICSEARCH_HOSTS')

    def __init__(self):
        if not self.elasticsearch_endpoint:
            log.error(f'elasticsearch endpoint missing: {self.elasticsearch_endpoint}')


class ConfigESSnapshotBot:
    def __init__(self):
        self.slack_name = 'Elasticsearch Elasticsearch Daily Monitor bot'
        self.elasticsearch_endpoint = ConfigES.elasticsearch_endpoint
        self.elasticsearch_repository = os.getenv('ELASTICSEARCH_REPOSITORY')
        self.snapshots_prefix = os.getenv('SNAPSHOTS_PREFIX')


class ConfigESJVMBot:
    def __init__(self):
        self.slack_name = 'Elasticsearch JVM Monitor bot'
        self.elasticsearch_endpoint = ConfigES.elasticsearch_endpoint


class ElasticsearchConfig:

    def __init__(self, proxy=None):
        self.hosts = []
        self.proxy = proxy

        hosts = ConfigES.elasticsearch_endpoint

        if hosts:

            if ',' in hosts:
                hosts = hosts.split(',')
            elif ' ' in hosts:
                hosts = hosts.split(' ')

            for host in hosts:
                host = Sanitation.no_spaces(host)
                host = Sanitation.no_quotes(host)
                self.hosts.append(host)
