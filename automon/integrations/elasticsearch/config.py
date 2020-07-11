import os

from automon.logger import Logging
from automon.helpers.sanitation import Sanitation as S

log = Logging('config')


class ElasticsearchConfig:
    def __init__(self, endpoints: str = None, proxy=None):
        self.es_hosts = S.list_from_string(endpoints) if endpoints else \
            S.list_from_string(os.getenv('ELASTICSEARCH_ENDPOINT')) or \
            S.list_from_string(os.getenv('ELASTICSEARCH_HOSTS'))
        self.es_proxy = proxy

        if not self.es_hosts:
            log.error(f'Missing {__name__} arg endpoints')


class SnapshotBot:
    def __init__(self):
        self.slack_name = 'Elasticsearch Daily Monitor bot'
        self.es_hosts = ElasticsearchConfig().es_hosts
        self.es_repository = os.getenv('ELASTICSEARCH_REPOSITORY')
        self.snapshots_prefix = os.getenv('SNAPSHOTS_PREFIX')


class JVMBot:
    def __init__(self):
        self.slack_name = 'Elasticsearch JVM Monitor bot'
        self.es_hosts = ElasticsearchConfig().es_hosts
