import requests
import elasticsearch

from datetime import datetime
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from .config import ElasticsearchConfig
from automon.helpers.sanitation import Sanitation

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class ElasticsearchClient(Elasticsearch):
    def __init__(
            self,
            host: str = None,
            cloud_id: str = None,
            user: str = None,
            password: str = None,
            api_key: tuple = None,
            api_key_id: str = None,
            api_key_secret: str = None,
            config: ElasticsearchConfig = None
    ):
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
                verify_certs=self.config.verify_certs
            )
            logger.info(f'Connected to elasticsearch: {client}')
            return client

        except Exception as e:
            logger.error(f'Cannot connect to elasticsearch: {self.config.ELASTICSEARCH_HOST}, {e}')

        return False

    def connected(self):
        """Check if connected"""
        if self.client:
            try:
                if self.client.ping():
                    return True
            except Exception as error:
                logger.error(f'{error}')
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
            response = self.client.index(index=index, body=doc, id=id)

            self.client.indices.refresh(index=index)
            self.success.append({'doc': doc, 'index': index, 'id': id, 'result': response})
            logger.debug(f'created document: {index} {id} {doc}')
            return response
        except Exception as e:
            logger.error(f'Create document failed: {e}')
            self.errors.append({'index': index, 'doc': doc, 'id': id, 'error': e})

    def delete_index(self, index: str, **kwargs):
        if self.connected():
            try:
                response = self.client.indices.delete(index=index, ignore=[400, 404], **kwargs)

                self.success.append({'delete index': index, 'result': response})
                logger.debug(f'deleted index: {index}')
                return response
            except Exception as error:
                self.errors.append({'index': index, 'error': error})
                logger.error(f'Delete index failed: {error}')

    def delete_document(self, index: str, id: str = None):
        if self.connected():
            try:
                response = self.client.delete(index=index, id=id, ignore=[400, 404])

                self.success.append({'index': index, 'id': id, 'result': response})
                logger.debug(f'deleted document: {index} {id}')
                return response
            except Exception as error:
                logger.error(f'Delete document failed: {error}')
                self.errors.append({'index': index, 'id': id, 'error': error})

    def get_indices(self) -> bool:
        if self.connected():
            try:
                response = self.client.indices.get('*')

                retrieved_indices = response
                self.indices = retrieved_indices
                logger.info(f'Retrieved {len(retrieved_indices)} indices')

                for i in retrieved_indices:
                    info = retrieved_indices.get(i)
                    date = int(info.get('settings').get('index').get('creation_date')) / 1000.0
                    date = datetime.fromtimestamp(date).strftime("%A, %B %d, %Y %I:%M:%S")
                    logger.debug(f'Index: (created: {date})\t{i}')

                self.success.append({'indices': retrieved_indices})
                logger.info(f'indices: {len(retrieved_indices)}')
                return response
            except Exception as error:
                logger.error(f'Failed to get indices: {error}')
                self.errors.append({'error': error})

    def info(self) -> bool:

        try:
            response = self.client.info()
            return response
        except Exception as e:
            logger.error(f'Failed to get info:{e}')
            self.errors.append({'error': e})

        return response

    def isConnected(self):
        return self.connected()

    def ping(self):
        if self.connected():
            try:
                self.client.ping()
                logger.debug(f'Ping successful')
                return True
            except Exception as e:
                self.errors.append({'error': e})
                logger.error(f'Ping failed: {e}')

        return False

    def rest(self, url: str) -> requests:
        try:
            if self.config.ELASTICSEARCH_USER and self.config.ELASTICSEARCH_PASSWORD:
                response = requests.get(url, auth=HTTPBasicAuth(
                    self.config.ELASTICSEARCH_USER,
                    self.config.ELASTICSEARCH_PASSWORD
                ))
            else:
                response = requests.get(url)

            self.success.append({'url': url, 'result': r})
            return response

        except Exception as e:
            logger.error(f'REST request failed: {e}')
            self.errors.append({'url': url, 'error': e})

        return False

    def search(self, search: dict = None, index: str = 'default'):

        if not search:
            search = {"query": {"match_all": {}}}

        try:
            response = self.client.search(index=index, body=search)

            self.success.append({'search': search, 'index': index, 'result': response})
            logger.debug(f'search :{search} {index}, result {response}')
            return True
        except Exception as error:
            logger.error(f'Search failed: {error}')
            self.errors.append({'search': search, 'index': index, 'error': error})
        return False

    def search_summary(self, **kwargs):

        response = self.search(kwargs)

        print(f"Got {response['hits']['total']['value']} Hits")

        for hit in response['hits']['hits']:
            print(f'{hit.get("_source")}')

        self.success.append({'result': response})
        logger.debug(f'search summary {response}')

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
    #         logger.debug(f'No indices found')
    #         return False
    #
    #     logger.info(f'Search found {num_indices} indices')
    #
    #     for index in retrieved_indices:
    #         logger.debug(index)
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
                response = self.client.indices.get(index_pattern)

                retrieved_indices = response
                num_indices = len(retrieved_indices)
                logger.info(f'Search found {num_indices} indices')
                self.success.append({'index pattern': index_pattern, 'result': retrieved_indices})
                logger.debug(f'search indices: {index_pattern}')
                return True

            except elasticsearch.exceptions.NotFoundError as e:
                logger.error(
                    f"You provided the index pattern '{index_pattern}', but returned no results")
                self.errors.append({'index pattern': index_pattern, 'error': e})
            except Exception as e:
                logger.error(f'Failed to search indices: {e}')
                self.errors.append({'index pattern': index_pattern, 'error': e})

        return False
