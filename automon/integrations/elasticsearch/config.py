import os
import logging

from elasticsearch import RequestsHttpConnection

from automon.log.logger import Logging
from automon.helpers.sanitation import Sanitation as S

logging.getLogger('elasticsearch').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)


class ElasticsearchConfig:
    def __init__(self, endpoints: str = None, proxy=None,
                 request_timeout: int = 1,
                 http_auth: tuple = None,
                 use_ssl: bool = True,
                 verify_certs: bool = True,
                 connection_class: RequestsHttpConnection = RequestsHttpConnection):
        self._log = Logging(ElasticsearchConfig.__name__, Logging.DEBUG)

        hosts = S.list_from_string(endpoints) or \
                S.list_from_string(os.getenv('ELASTICSEARCH_HOSTS')) or None
        # hosts = [{'host': x} for x in hosts]
        self.es_hosts = hosts
        self.ELASTICSEARCH_HOSTS = self.es_hosts
        self.ELASTICSEARCH_USER = os.getenv('ELASTICSEARCH_USER') or ''
        self.ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD') or ''

        self.es_proxy = proxy
        self.request_timeout = request_timeout

        if self.ELASTICSEARCH_USER and self.ELASTICSEARCH_PASSWORD:
            self.http_auth = (self.ELASTICSEARCH_USER, self.ELASTICSEARCH_PASSWORD)
        else:
            self.http_auth = http_auth

        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.connection_class = connection_class

        if not self.es_hosts:
            self._log.error(f'Missing ELASTICSEARCH_HOSTS')

    def __eq__(self, other):
        if not isinstance(other, ElasticsearchConfig):
            self._log.error(f'Not implemented')
            return NotImplemented

        return self.es_hosts == other.es_hosts


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
