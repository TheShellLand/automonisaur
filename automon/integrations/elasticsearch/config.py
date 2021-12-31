import os
import logging

from elasticsearch import RequestsHttpConnection

from automon.log import Logging
from automon.helpers.sanitation import Sanitation as S

logging.getLogger('elasticsearch').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)


class ElasticsearchConfig:
    def __repr__(self):
        return f'{self.ELASTICSEARCH_HOSTS}'

    def __init__(self, hosts: str = None,
                 cloud_id: str = None,
                 user: str = None,
                 password: str = None,
                 api_key: tuple = None,
                 api_key_id: str = None,
                 api_key_secret: str = None,
                 ELASTICSEARCH_USER: str = None,
                 ELASTICSEARCH_PASSWORD: str = None,
                 request_timeout: int = 1,
                 http_auth: tuple = None,
                 use_ssl: bool = True,
                 verify_certs: bool = True,
                 connection_class: RequestsHttpConnection = None,
                 proxy=None):
        """elasticsearch config"""

        self._log = Logging(ElasticsearchConfig.__name__, Logging.DEBUG)

        # hosts
        self.ELASTICSEARCH_HOSTS = hosts or os.getenv('ELASTICSEARCH_HOSTS') or None
        self.ELASTICSEARCH_HOSTS = S.list_from_string(self.ELASTICSEARCH_HOSTS)
        self.es_hosts = self.ELASTICSEARCH_HOSTS
        self.ELASTICSEARCH_CLOUD_ID = cloud_id or os.getenv('ELASTICSEARCH_CLOUD_ID')

        # auth
        self.ELASTICSEARCH_USER = user or ELASTICSEARCH_USER or os.getenv('ELASTICSEARCH_USER') or ''
        self.ELASTICSEARCH_PASSWORD = password or ELASTICSEARCH_PASSWORD \
                                      or os.getenv('ELASTICSEARCH_PASSWORD') or ''
        self.ELASTICSEARCH_API_KEY = api_key or os.getenv('ELASTICSEARCH_API_KEY')
        self.ELASTICSEARCH_API_KEY_ID = api_key_id or os.getenv('ELASTICSEARCH_API_KEY_ID')
        self.ELASTICSEARCH_API_KEY_SECRET = api_key_secret or os.getenv('ELASTICSEARCH_API_KEY_SECRET')

        if self.ELASTICSEARCH_API_KEY_ID and self.ELASTICSEARCH_API_KEY_SECRET \
                and not self.ELASTICSEARCH_API_KEY:
            self.ELASTICSEARCH_API_KEY = (self.ELASTICSEARCH_API_KEY_ID, self.ELASTICSEARCH_API_KEY_SECRET)

        # options
        self.ELASTICSEARCH_PROXY = proxy or os.getenv('ELASTICSEARCH_PROXY')
        self.ELASTICSEARCH_REQUEST_TIMEOUT = request_timeout or os.getenv('ELASTICSEARCH_REQUEST_TIMEOUT')
        self.request_timeout = self.ELASTICSEARCH_REQUEST_TIMEOUT
        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.connection_class = connection_class or RequestsHttpConnection

        if self.ELASTICSEARCH_USER and self.ELASTICSEARCH_PASSWORD:
            self.http_auth = (self.ELASTICSEARCH_USER, self.ELASTICSEARCH_PASSWORD)
        else:
            self.http_auth = http_auth

        # if not self.ELASTICSEARCH_HOSTS:
        #     self._log.error(f'Missing ELASTICSEARCH_HOSTS')

    def __eq__(self, other):
        if not isinstance(other, ElasticsearchConfig):
            self._log.warn(f'Not implemented')
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
