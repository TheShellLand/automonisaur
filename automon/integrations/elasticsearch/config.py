import os
import logging

from elasticsearch import RequestsHttpConnection

from automon.log.logger import Logging
from automon.helpers.sanitation import Sanitation as S

logging.getLogger('elasticsearch').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)


class ElasticsearchConfig:
    def __init__(self, endpoints: str = None, proxy=None,
                 ELASTICSEARCH_USER: str = None,
                 ELASTICSEARCH_PASSWORD: str = None,
                 request_timeout: int = 1,
                 http_auth: tuple = None,
                 use_ssl: bool = True,
                 verify_certs: bool = True,
                 connection_class: RequestsHttpConnection = None):
        self._log = Logging(ElasticsearchConfig.__name__, Logging.DEBUG)

        self.ELASTICSEARCH_HOSTS = endpoints or os.getenv('ELASTICSEARCH_HOSTS') or None
        self.ELASTICSEARCH_USER = ELASTICSEARCH_USER or os.getenv('ELASTICSEARCH_USER') or ''
        self.ELASTICSEARCH_PASSWORD = ELASTICSEARCH_PASSWORD or os.getenv('ELASTICSEARCH_PASSWORD') or ''

        self.es_hosts = S.list_from_string(endpoints) or S.list_from_string(self.ELASTICSEARCH_HOSTS)
        self.es_proxy = proxy
        self.request_timeout = request_timeout

        if self.ELASTICSEARCH_USER and self.ELASTICSEARCH_PASSWORD:
            self.http_auth = (self.ELASTICSEARCH_USER, self.ELASTICSEARCH_PASSWORD)
        else:
            self.http_auth = http_auth

        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.connection_class = connection_class or RequestsHttpConnection

        if not self.ELASTICSEARCH_HOSTS:
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
