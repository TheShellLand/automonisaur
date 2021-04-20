import requests
import elasticsearch

from datetime import datetime
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch

from automon.log.logger import Logging
from automon.integrations.elasticsearch.config import ElasticsearchConfig
from automon.helpers.sanitation import Sanitation


class ElasticsearchClient(ElasticsearchConfig):
    def __init__(self, config: ElasticsearchConfig = None):
        self._log = Logging(ElasticsearchClient.__name__, Logging.DEBUG)

        self.config = config or ElasticsearchConfig()
        self.client = Elasticsearch(hosts=self.config.es_hosts,
                                    request_timeout=self.config.request_timeout,
                                    http_auth=self.config.http_auth,
                                    use_ssl=self.config.use_ssl,
                                    verify_certs=self.config.verify_certs,
                                    connection_class=self.config.connection_class)
        self.connected = self.client.ping() if self.config.es_hosts else False

        self.indices = []

    def rest(self, url: str) -> requests:
        try:
            if self.config.ELASTICSEARCH_USER and self.config.ELASTICSEARCH_PASSWORD:
                return requests.get(url, auth=HTTPBasicAuth(self.config.ELASTICSEARCH_USER,
                                                            self.config.ELASTICSEARCH_PASSWORD))
            else:
                return requests.get(url)

        except Exception as e:
            self._log.error(f'REST request failed: {e}')
            return False

    def ping(self):
        if self.connected:
            try:
                return self.client.ping()
            except Exception as e:
                self._log.error(f'Ping failed: {e}')
                return False

        return False

    def delete_index(self, index: str):
        if self.connected and index:
            try:
                return self.client.delete(index=Sanitation.ascii_numeric_only(index))
            except Exception as e:
                self._log.error(f'Delete index failed: {e}')
                return False

        return False

    def create_document(self, doc: dict, index: str = 'default', id: str = None):
        # doc = {
        #     'author': 'kimchy',
        #     'text': 'Elasticsearch: cool. bonsai cool.',
        #     'timestamp': datetime.now(),
        # }

        self.client.index(index=index, body=doc, id=id)
        return self.client.indices.refresh(index=index)

    def search(self, search: dict = None, index: str = 'default'):

        if not search:
            search = {"query": {"match_all": {}}}

        return self.client.search(index=index, body=search)

    def search_summary(self, **kwargs):

        res = self.search(kwargs)

        print(f"Got {res['hits']['total']['value']} Hits")

        for hit in res['hits']['hits']:
            print(f'{hit.get("_source")}')

        return True

    # def delete_indices(self, index_pattern):
    #     """Requires user interaction"""
    #
    #     if not self.connected:
    #         return False
    #
    #     retrieved_indices = [x for x in self.client.search_indices(index_pattern).keys()]
    #     num_indices = len(retrieved_indices)
    #
    #     if not num_indices:
    #         self._log.debug(f'No indices found')
    #         return False
    #
    #     self._log.info(f'Search found {num_indices} indices')
    #
    #     for index in retrieved_indices:
    #         self._log.debug(index)
    #
    #     # TODO: Find a way to undo index deletions
    #     #       One way could be to rename the indices and store a link to the new
    #     #       indices in a node of deleted indices
    #     if num_indices < 2:
    #         msg = f"\nYOU'RE ABOUT TO DELETE {num_indices} INDEX! ARE YOU SURE YOU WANT TO CONTINUE? "
    #     elif num_indices > 1:
    #         msg = f"\nYOU'RE ABOUT TO DELETE {num_indices} INDICES! ARE YOU SURE YOU WANT TO CONTINUE? "
    #     msg += 'THIS CANNOT BE UNDONE! DECIDED WISELY [y/N]'
    #     print(msg)
    #
    #     answer = str(input()).lower()
    #
    #     if not answer:
    #         answer = 'N'
    #
    #     if answer == 'y':
    #         for index in retrieved_indices:
    #             msg = f'Deleting {index}...'
    #             print(msg, end='')
    #             # Delete the index
    #             self.delete_index(index)
    #             print('done')
    #     else:
    #         print('Whew, you might have just blew it, if you had said yes')

    def search_indices(self, index_pattern):
        if self.connected and index_pattern:
            try:
                retrieved_indices = self.client.indices.get(index_pattern)
                num_indices = len(retrieved_indices)
                self._log.info(f'Search found {num_indices} indices')
                return retrieved_indices
            except elasticsearch.exceptions.NotFoundError:
                self._log.error(
                    f"You provided the index pattern '{index_pattern}', but returned no results")
            except Exception as e:
                self._log.error(f'Failed to search indices: {e}')

        return False

    def get_indices(self):
        if self.connected:
            try:
                retrieved_indices = self.client.indices.get('*')
                self.indices.extend(retrieved_indices)
                self._log.info(f'Retrieved {len(retrieved_indices)} indices')
                for i in retrieved_indices:
                    info = retrieved_indices.get(i)
                    date = int(info.get('settings').get('index').get('creation_date')) / 1000.0
                    date = datetime.fromtimestamp(date).strftime("%A, %B %d, %Y %I:%M:%S")
                    self._log.debug(f'Index: (created: {date})\t{i}')
                return True
            except Exception as e:
                self._log.error(f'Failed to get indices: {e}')

        return False
