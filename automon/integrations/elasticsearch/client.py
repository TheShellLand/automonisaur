import requests
import elasticsearch

from automon.log.logger import Logging
from automon.integrations.elasticsearch.config import ElasticsearchConfig


class ElasticsearchClient(ElasticsearchConfig):
    def __init__(self, config: ElasticsearchConfig = None):
        self._log = Logging(ElasticsearchClient.__name__, Logging.DEBUG)

        self.config = config if config == ElasticsearchConfig else ElasticsearchConfig()
        self.client = self.config.Elasticsearch
        self.connected = self.client.ping() if self.client else False

        self.indices = []

    def rest(self, url):
        if not self.connected:
            return False

        request = requests.get(url)

        self._log.info(f'Status code: {request.status_code}')

        return request.content

    def ping(self):
        if not self.connected:
            return False
        return self.client.ping()

    def delete_index(self, index):
        if not self.connected:
            return False
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
