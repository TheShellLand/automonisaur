import json

from automon import log
from automon.integrations.elasticsearch.metrics import Cluster
from automon.integrations.elasticsearch.config import ElasticsearchConfig
from automon.integrations.elasticsearch.client import ElasticsearchClient

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class ElasticsearchJvmMonitor:
    def __init__(self, config: ElasticsearchConfig = None):

        self._config = config if isinstance(config, ElasticsearchConfig) else ElasticsearchConfig()
        self._client = ElasticsearchClient(config) if isinstance(config, ElasticsearchConfig) else ElasticsearchClient()

        self._endpoint = self._client.config.ELASTICSEARCH_HOST

    def _get_all_stats(self):
        if self._client.connected():
            for endpoint in self._endpoint:
                try:
                    request = self._client.rest(f'{endpoint}/_nodes/stats?pretty')
                    request_json = request.text
                    return json.loads(request_json)
                except Exception as e:
                    logger.error(f'Failed to get all stats: {e}')
                    return False

        return False

    def _get_all_jvm_metrics(self):
        if self._client.connected():
            try:
                return Cluster(self._get_all_stats())
            except Exception as e:
                logger.error(f'Failed to get jvm metrics: {e}')

        return False

    def read_file(self, file):
        try:
            with open(file, 'rb') as stats:
                return json.load(stats)
        except Exception as e:
            logger.error(f'Failed to read file: {e}')

    def get_metrics(self):
        if self._client.connected():
            try:
                return self._get_all_jvm_metrics()
            except Exception as e:
                logger.error(f'Failed to get metrics: {e}')

        return False
