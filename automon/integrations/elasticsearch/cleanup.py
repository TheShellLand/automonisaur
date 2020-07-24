from automon.log.logger import Logging
from automon.integrations.elasticsearch.client import ElasticsearchClient


class Cleanup:

    def __init__(self):
        self._log = Logging(Cleanup.__name__, Logging.DEBUG)
        self.client = ElasticsearchClient()

    def get_indices(self):
        return self.client.get_indices()

    def search_indices(self, index_pattern):
        return self.client.search_indices(index_pattern)

    # def delete_indices(self, index_pattern):
    #     return self.client.delete_indices(index_pattern)
