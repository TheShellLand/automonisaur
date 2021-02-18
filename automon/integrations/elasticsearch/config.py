import os

from elasticsearch import RequestsHttpConnection

from automon.log.logger import Logging
from automon.helpers.sanitation import Sanitation as S


class ElasticsearchConfig:
    def __init__(self, endpoints: str = None, proxy=None,
                 request_timeout: int = 1,
                 http_auth=None,
                 use_ssl: bool = True,
                 verify_certs: bool = True,
                 connection_class: RequestsHttpConnection = RequestsHttpConnection):
        self._log = Logging(ElasticsearchConfig.__name__, Logging.DEBUG)

        self.es_hosts = S.list_from_string(endpoints) or \
            S.list_from_string(os.getenv('ELASTICSEARCH_ENDPOINT')) or \
            S.list_from_string(os.getenv('ELASTICSEARCH_HOSTS')) or None

        self.es_proxy = proxy
        self.request_timeout = request_timeout
        self.http_auth = http_auth
        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.connection_class = connection_class

        if not self.es_hosts:
            self._log.error(f'Missing ELASTICSEARCH_ENDPOINT')

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
