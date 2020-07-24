import json

from automon.log import Logging
from automon.integrations.elasticsearch.metrics import Cluster
from automon.integrations.elasticsearch.config import ElasticsearchConfig
from automon.integrations.elasticsearch.client import ElasticsearchClient


class ElasticsearchJvmMonitor:
    def __init__(self, config: ElasticsearchConfig = None):
        self._log = Logging(ElasticsearchJvmMonitor.__name__, Logging.DEBUG)

        self._config = config if isinstance(config, ElasticsearchConfig) else ElasticsearchConfig()
        self._client = ElasticsearchConfig(config) \
            if config == ElasticsearchConfig else ElasticsearchClient()

        self._endpoint = self._client.config.es_hosts

    def _get_all_stats(self):
        try:
            request_json = self._client.rest(f'{self._endpoint}/_nodes/stats?pretty')
            return json.loads(request_json)
        except Exception as e:
            self._log.error(f'Failed to get all stats: {e}')
            return False

    def _get_all_jvm_metrics(self):
        try:
            return Cluster(self._get_all_stats())
        except Exception as e:
            self._log.error(f'Failed to get jvm metrics: {e}')

    def read_file(self, file):
        try:
            with open(file, 'rb') as stats:
                return json.load(stats)
        except Exception as e:
            self._log.error(f'Failed to read file: {e}')

    def get_metrics(self):
        try:
            return self._get_all_jvm_metrics()
        except Exception as e:
            self._log.error(f'Failed to get metrics: {e}')
