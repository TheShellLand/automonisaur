import os
import elasticsearch

from elasticsearch import Elasticsearch, RequestsHttpConnection

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

        self.es_hosts = S.list_from_string(endpoints) if endpoints else \
            S.list_from_string(os.getenv('ELASTICSEARCH_ENDPOINT')) or \
            S.list_from_string(os.getenv('ELASTICSEARCH_HOSTS')) or None

        self.es_proxy = proxy
        self.request_timeout = request_timeout
        self.http_auth = http_auth
        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.connection_class = connection_class

        if self.es_hosts:
            self.Elasticsearch = Elasticsearch(
                hosts=self.es_hosts,
                request_timeout=self.request_timeout,
                http_auth=self.http_auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                connection_class=self.connection_class)

        else:
            self.Elasticsearch = False
            self._log.error(f'Missing ELASTICSEARCH_ENDPOINT, ELASTICSEARCH_ENDPOINT')


class ElasticsearchClient(ElasticsearchConfig):
    def __init__(self):
        self._log = Logging(ElasticsearchClient.__name__, Logging.DEBUG)

        self.config = ElasticsearchConfig()
        self.client = self.config.Elasticsearch
        self.connected = self.client.ping() if self.client else False

        self.indices = []

    def ping(self):
        if not self.connected:
            return False
        return self.client.ping()

    def delete_index(self, index):
        self.client.delete(index)

    def delete_indices(self, index_pattern):
        """Requires user interaction"""

        if not self.connected:
            return False

        retrieved_indices = [x for x in self.client.search_indices(index_pattern).keys()]
        num_indices = len(retrieved_indices)

        if not num_indices:
            self._log.debug(f'No indices found')
            return False

        self._log.info(f'Search found {num_indices} indices')

        for index in retrieved_indices:
            self._log.debug(index)

        # TODO: Find a way to undo index deletions
        #       One way could be to rename the indices and store a link to the new
        #       indices in a node of deleted indices
        if num_indices < 2:
            msg = f"\nYOU'RE ABOUT TO DELETE {num_indices} INDEX! ARE YOU SURE YOU WANT TO CONTINUE? "
        elif num_indices > 1:
            msg = f"\nYOU'RE ABOUT TO DELETE {num_indices} INDICES! ARE YOU SURE YOU WANT TO CONTINUE? "
        msg += 'THIS CANNOT BE UNDONE! DECIDED WISELY [y/N]'
        print(msg)

        answer = str(input()).lower()

        if not answer:
            answer = 'N'

        if answer == 'y':
            for index in retrieved_indices:
                msg = f'Deleting {index}...'
                print(msg, end='')
                # Delete the index
                self.delete_index(index)
                print('done')
        else:
            print('Whew, you might have just blew it, if you had said yes')

    def search_indices(self, index_pattern):
        if not self.connected:
            return False

        try:
            retrieved_indices = self.client.indices.get(index_pattern)
            num_indices = len(retrieved_indices)
            self._log.info(f'Search found {num_indices} indices')
            return retrieved_indices
        except elasticsearch.exceptions.NotFoundError:
            self._log.error(
                f"You provided the index pattern '{index_pattern}', but returned no results")

    def get_indices(self):
        if not self.connected:
            return False

        retrieved_indices = self.client.indices.get('*')
        num_indices = len(retrieved_indices)

        self.indices.extend(retrieved_indices)
        self._log.info(f'Retrieved {num_indices} indices')


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
