from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.integrations.elasticsearch.client import ElasticsearchClient

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class Cleanup:

    def __init__(self):
        self.client = ElasticsearchClient()

    def get_indices(self):
        return self.client.get_indices()

    def search_indices(self, index_pattern):
        return self.client.search_indices(index_pattern)

    # def delete_indices(self, index_pattern):
    #     return self.client.delete_indices(index_pattern)
