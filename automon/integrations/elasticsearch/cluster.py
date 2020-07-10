from automon.integrations.elasticsearch.metric import Metric


class Cluster:
    def __init__(self, raw_metrics):
        self._all_metrics = raw_metrics
        self._nodes = {
            'total': self._all_metrics['_nodes']['total'],
            'successful': self._all_metrics['_nodes']['successful'],
            'failed': self._all_metrics['_nodes']['failed']
        }

        self.cluster_name = self._all_metrics['cluster_name']
        self.nodes = []
        self.metrics = []

        for node in self._all_metrics['nodes'].items():
            self.nodes.append(node[1])

        for metric in self.nodes:
            self.metrics.append(Metric(metric))
