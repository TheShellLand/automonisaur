import requests
import elasticsearch

from datetime import datetime
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch

from automon.log import Logging
from .config import ElasticsearchConfig
from automon.helpers.sanitation import Sanitation


class ElasticsearchClient(Elasticsearch):
    def __init__(self, host: str = None,
                 cloud_id: str = None,
                 user: str = None,
                 password: str = None,
                 api_key: tuple = None,
                 api_key_id: str = None,
                 api_key_secret: str = None,
                 config: ElasticsearchConfig = None):
        """elasticsearch wrapper

        :param host: str
        :param cloud_id: str
        :param user: str
        :param password: str
        :param api_key: base64 str
        :param api_key_id: str
        :param api_key_secret: str
        :param config: class ElasticsearchConfig
        """

        self._log = Logging(ElasticsearchClient.__name__, Logging.DEBUG)

        self.config = config or ElasticsearchConfig(
            host=host,
            cloud_id=cloud_id,
            user=user,
            password=password,
            api_key=api_key,
            api_key_id=api_key_id,
            api_key_secret=api_key_secret)

        self.client = self._client()

        self.indices = []
        self.success = []
        self.errors = []
        self.results = None

    def __repr__(self):
        return f'{self.client}, indices: {self.indices}, errors: {self.errors}, {self.config}'

    def _client(self):
        """Elasticsearch client"""
        try:
            client = Elasticsearch(
                hosts=self.config.ELASTICSEARCH_HOST,
                cloud_id=self.config.ELASTICSEARCH_CLOUD_ID,
                api_key=self.config.ELASTICSEARCH_API_KEY,
                request_timeout=self.config.ELASTICSEARCH_REQUEST_TIMEOUT,
                http_auth=self.config.http_auth,
                use_ssl=self.config.use_ssl,
                verify_certs=self.config.verify_certs,
                connection_class=self.config.connection_class)
            self._log.info(f'Connected to elasticsearch: {client}')
            return client

        except Exception as e:
            self._log.error(f'Cannot connect to elasticsearch: {self.config.ELASTICSEARCH_HOST}, {e}')

        return False

    def connected(self):
        """Check if connected"""
        if self.client:
            try:
                if self.client.ping():
                    return True
            except Exception as e:
                self._log.error(f'{e}', enable_traceback=False)
        return False

    def create_document(self, doc: dict, index: str = 'default', id: str = None):
        """Create document

        :param doc:
        :param index:
        :param id:
        :return: bool
        """
        # doc = {
        #     'author': 'kimchy',
        #     'text': 'Elasticsearch: cool. bonsai cool.',
        #     'timestamp': datetime.now(),
        # }

        try:
            self.results = self.client.index(index=index, body=doc, id=id)

            r = self.results
            self.client.indices.refresh(index=index)
            self.success.append({'doc': doc, 'index': index, 'id': id, 'result': r})
            self._log.debug(f'created document: {index} {id} {doc}')
            return True
        except Exception as e:
            self._log.error(f'Create document failed: {e}')
            self.errors.append({'index': index, 'doc': doc, 'id': id, 'error': e})
        return False

    def delete_index(self, index: str, **kwargs):
        if self.connected():
            try:
                self.results = self.client.indices.delete(index=index, ignore=[400, 404], **kwargs)

                r = self.results
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
                self.results = self.client.delete(index=index, id=id, ignore=[400, 404])

                r = self.results
                self.success.append({'index': index, 'id': id, 'result': r})
                self._log.debug(f'deleted document: {index} {id}')
                return True
            except Exception as e:
                self._log.error(f'Delete document failed: {e}')
                self.errors.append({'index': index, 'id': id, 'error': e})

        return False

    def get_indices(self) -> bool:
        if self.connected():
            try:
                self.results = self.client.indices.get('*')

                retrieved_indices = self.results
                self.indices = retrieved_indices
                self._log.info(f'Retrieved {len(retrieved_indices)} indices')

                for i in retrieved_indices:
                    info = retrieved_indices.get(i)
                    date = int(info.get('settings').get('index').get('creation_date')) / 1000.0
                    date = datetime.fromtimestamp(date).strftime("%A, %B %d, %Y %I:%M:%S")
                    self._log.debug(f'Index: (created: {date})\t{i}')

                self.success.append({'indices': retrieved_indices})
                self._log.info(f'indices: {len(retrieved_indices)}')
                return True
            except Exception as e:
                self._log.error(f'Failed to get indices: {e}')
                self.errors.append({'error': e})

        return False

    def info(self) -> bool:

        try:
            self.results = self.client.info()
            return True
        except Exception as e:
            self._log.error(f'Failed to get info:{e}')
            self.errors.append({'error': e})

        return False

    def isConnected(self):
        return self.connected()

    def ping(self):
        if self.connected():
            try:
                self.client.ping()
                self._log.debug(f'Ping successful')
                return True
            except Exception as e:
                self.errors.append({'error': e})
                self._log.error(f'Ping failed: {e}')

        return False

    def rest(self, url: str) -> requests:
        try:
            if self.config.ELASTICSEARCH_USER and self.config.ELASTICSEARCH_PASSWORD:
                self.results = requests.get(url, auth=HTTPBasicAuth(
                    self.config.ELASTICSEARCH_USER,
                    self.config.ELASTICSEARCH_PASSWORD
                ))
                r = self.results
            else:
                self.results = requests.get(url)
                r = self.results

            self.success.append({'url': url, 'result': r})
            return r

        except Exception as e:
            self._log.error(f'REST request failed: {e}')
            self.errors.append({'url': url, 'error': e})

        return False

    def search(self, search: dict = None, index: str = 'default'):

        if not search:
            search = {"query": {"match_all": {}}}

        try:
            self.results = self.client.search(index=index, body=search)

            r = self.results
            self.success.append({'search': search, 'index': index, 'result': r})
            self._log.debug(f'search :{search} {index}, result {r}')
            return True
        except Exception as e:
            self._log.error(f'Search failed: {e}')
            self.errors.append({'search': search, 'index': index, 'error': e})
        return False

    def search_summary(self, **kwargs):

        self.results = self.search(kwargs)

        res = self.results
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
                self.results = self.client.indices.get(index_pattern)

                retrieved_indices = self.results
                num_indices = len(retrieved_indices)
                self._log.info(f'Search found {num_indices} indices')
                self.success.append({'index pattern': index_pattern, 'result': retrieved_indices})
                self._log.debug(f'search indices: {index_pattern}')
                return True

            except elasticsearch.exceptions.NotFoundError as e:
                self._log.error(
                    f"You provided the index pattern '{index_pattern}', but returned no results")
                self.errors.append({'index pattern': index_pattern, 'error': e})
            except Exception as e:
                self._log.error(f'Failed to search indices: {e}')
                self.errors.append({'index pattern': index_pattern, 'error': e})

        return False
