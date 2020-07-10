import json
import requests

from automon.integrations.elasticsearch.cluster import Cluster


class ElasticsearchJvmMonitor:
    def __init__(self, elasticsearch_endpoint):

        self.endpoint = elasticsearch_endpoint
        self._all_stats = None

    def _get_all_stats(self, file=None):

        if file:
            with open(file, 'rb') as stats:
                self._all_stats = json.load(stats)
        else:
            url = '{endpoint}/_nodes/stats?pretty'.format(endpoint=self.endpoint)

            request_json = requests.get(url).content
            self._all_stats = json.loads(request_json)

    def _get_all_jvm_metrics(self):
        metrics = self._all_stats
        self.cluster = Cluster(metrics)

    def read_file(self, file):
        self._get_all_stats(file=file)

    def get_metrics(self):
        if not self._all_stats:
            self._get_all_stats()

        self._get_all_jvm_metrics()
