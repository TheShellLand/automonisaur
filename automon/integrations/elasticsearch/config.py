import os

from elasticsearch import Elasticsearch, RequestsHttpConnection

from automon.log.logger import Logging
from automon.helpers.sanitation import Sanitation as S

log = Logging(__name__)


class ElasticsearchConfig:
    def __init__(self, endpoints: str = None, proxy=None,
                 request_timeout: int = 5,
                 http_auth=None,
                 use_ssl: bool = True,
                 verify_certs: bool = True,
                 connection_class: RequestsHttpConnection = RequestsHttpConnection):
        self.es_hosts = S.list_from_string(endpoints) if endpoints else \
            S.list_from_string(os.getenv('ELASTICSEARCH_ENDPOINT')) or \
            S.list_from_string(os.getenv('ELASTICSEARCH_HOSTS'))
        self.es_proxy = proxy
        self.request_timeout = request_timeout
        self.http_auth = http_auth
        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.connection_class = connection_class

        if not self.es_hosts:
            log.error('Missing endpoints')

    def Elasticsearch(self):
        if self.es_hosts:
            return Elasticsearch(
                hosts=self.es_hosts,
                request_timeout=self.request_timeout,
                http_auth=self.http_auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                connection_class=self.connection_class)
        else:
            return False


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
