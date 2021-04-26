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

        self._config = config or ElasticsearchConfig()
        self._client = Elasticsearch(hosts=self._config.es_hosts,
                                     request_timeout=self._config.request_timeout,
                                     http_auth=self._config.http_auth,
                                     use_ssl=self._config.use_ssl,
                                     verify_certs=self._config.verify_certs,
                                     connection_class=self._config.connection_class)
        self.indices = []
        self.success = []
        self.errors = []

    def __repr__(self):
        return f'{self._config}, {self._client}, indices: {self.indices}, errors: {self.errors}'

    def connected(self):
        if self._config.es_hosts:
            if self._client.ping():
                return True
        return False

    def rest(self, url: str) -> requests:
        try:
            if self._config.ELASTICSEARCH_USER and self._config.ELASTICSEARCH_PASSWORD:
                r = requests.get(url, auth=HTTPBasicAuth(
                    self._config.ELASTICSEARCH_USER,
                    self._config.ELASTICSEARCH_PASSWORD
                ))
            else:
                r = requests.get(url)

            self.success.append({'url': url, 'result': r})
            return r

        except Exception as e:
            self._log.error(f'REST request failed: {e}')
            self.errors.append({'url': url, 'error': e})

        return False

    def ping(self):
        if self.connected():
            try:
                self._client.ping()
                self._log.debug(f'Ping successful')
                return True
            except Exception as e:
                self.errors.append({'error': e})
                self._log.error(f'Ping failed: {e}')

        return False

    def delete_index(self, index: str, **kwargs):
        if self.connected():
            try:
                r = self._client.indices.delete(index=index, ignore=[400, 404], **kwargs)
                self.success.append({'delete index': index, 'result': r})
                self._log.debug(f'deleted index: {index}')
                return True
            except Exception as e:
                self.errors.append({'index': index, 'error': e})
                self._log.error(f'Delete index failed: {e}')

        return False

    def delete_document(self, index: str, id: str = None):
        if self.connected():
            try:
                r = self._client.delete(index=index, id=id, ignore=[400, 404])
                self.success.append({'index': index, 'id': id, 'result': r})
                self._log.debug(f'deleted document: {index} {id}')
                return True
            except Exception as e:
                self._log.error(f'Delete document failed: {e}')
                self.errors.append({'index': index, 'id': id, 'error': e})

        return False

    def create_document(self, doc: dict, index: str = 'default', id: str = None):
        # doc = {
        #     'author': 'kimchy',
        #     'text': 'Elasticsearch: cool. bonsai cool.',
        #     'timestamp': datetime.now(),
        # }

        try:
            r = self._client.index(index=index, body=doc, id=id)
            self._client.indices.refresh(index=index)
            self.success.append({'doc': doc, 'index': index, 'id': id, 'result': r})
            self._log.debug(f'created document: {index} {id} {doc}')
            return True
        except Exception as e:
            self._log.error(f'Create document failed: {e}')
            self.errors.append({'index': index, 'doc': doc, 'id': id, 'error': e})
        return False

    def search(self, search: dict = None, index: str = 'default'):

        if not search:
            search = {"query": {"match_all": {}}}

        try:
            r = self._client.search(index=index, body=search)
            self.success.append({'search': search, 'index': index, 'result': r})
            self._log.debug(f'search :{search} {index}, result {r}')
            return True
        except Exception as e:
            self._log.error(f'Search failed: {e}')
            self.errors.append({'search': search, 'index': index, 'error': e})
        return False

    def search_summary(self, **kwargs):

        res = self.search(kwargs)

        print(f"Got {res['hits']['total']['value']} Hits")

        for hit in res['hits']['hits']:
            print(f'{hit.get("_source")}')

        self.success.append({'result': res})
        self._log.debug(f'search summary {res}')

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
        if self.connected() and index_pattern:
            try:
                retrieved_indices = self._client.indices.get(index_pattern)
                num_indices = len(retrieved_indices)
                self._log.info(f'Search found {num_indices} indices')
                self.success.append({'index pattern': index_pattern, 'result': retrieved_indices})
                self._log.debug(f'search indices: {index_pattern}')
                return retrieved_indices
            except elasticsearch.exceptions.NotFoundError as e:
                self._log.error(
                    f"You provided the index pattern '{index_pattern}', but returned no results")
                self.errors.append({'index pattern': index_pattern, 'error': e})
            except Exception as e:
                self._log.error(f'Failed to search indices: {e}')
                self.errors.append({'index pattern': index_pattern, 'error': e})

        return False

    def get_indices(self):
        if self.connected():
            try:
                retrieved_indices = self._client.indices.get('*')
                self.indices.extend(retrieved_indices)
                self._log.info(f'Retrieved {len(retrieved_indices)} indices')
                for i in retrieved_indices:
                    info = retrieved_indices.get(i)
                    date = int(info.get('settings').get('index').get('creation_date')) / 1000.0
                    date = datetime.fromtimestamp(date).strftime("%A, %B %d, %Y %I:%M:%S")
                    self._log.debug(f'Index: (created: {date})\t{i}')
                self.success.append({'indices': retrieved_indices})
                self._log.debug(f'get indices: {retrieved_indices}')
                return True
            except Exception as e:
                self._log.error(f'Failed to get indices: {e}')
                self.errors.append({'error': e})

        return False
