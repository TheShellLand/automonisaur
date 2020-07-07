import json
import datetime
import requests


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


class Metric:
    """

    Example JVM Metric for one node:

    "jvm" : {
        "timestamp" : 1571330469200,
        "uptime_in_millis" : 12251148809,
        "mem" : {
          "heap_used_in_bytes" : 27551308288,
          "heap_used_percent" : 82,
          "heap_committed_in_bytes" : 33216266240,
          "heap_max_in_bytes" : 33216266240,
          "non_heap_used_in_bytes" : 162665664,
          "non_heap_committed_in_bytes" : 204083200,
          "pools" : {
            "young" : {
              "used_in_bytes" : 130099216,
              "max_in_bytes" : 558432256,
              "peak_used_in_bytes" : 558432256,
              "peak_max_in_bytes" : 558432256
            },
            "survivor" : {
              "used_in_bytes" : 1132144,
              "max_in_bytes" : 69730304,
              "peak_used_in_bytes" : 69730304,
              "peak_max_in_bytes" : 69730304
            },
            "old" : {
              "used_in_bytes" : 27420076928,
              "max_in_bytes" : 32588103680,
              "peak_used_in_bytes" : 30895029472,
              "peak_max_in_bytes" : 32588103680
            }
          }
        },
        "threads" : {
          "count" : 141,
          "peak_count" : 223
        },
        "gc" : {
          "collectors" : {
            "young" : {
              "collection_count" : 533686,
              "collection_time_in_millis" : 37099480
            },
            "old" : {
              "collection_count" : 75872,
              "collection_time_in_millis" : 9588732
            }
          }
        },
        "buffer_pools" : {
          "mapped" : {
            "count" : 7988,
            "used_in_bytes" : 3715149748692,
            "total_capacity_in_bytes" : 3715149748692
          },
          "direct" : {
            "count" : 10146,
            "used_in_bytes" : 166764364,
            "total_capacity_in_bytes" : 166764363
          }
        },
        "classes" : {
          "current_loaded_count" : 17808,
          "total_loaded_count" : 18183,
          "total_unloaded_count" : 375
        }
      },


    """

    def __init__(self, node):
        self._node = node
        self.node_name = self._node['name']

        self.jvm = self._node['jvm']
        self.heap_used_percent = self.jvm['mem']['heap_used_percent']

        self._mem = self.jvm['mem']
        self._timestamp = self.jvm['timestamp']
        self._uptime_in_millis = self.jvm['uptime_in_millis']
        self._gc = self.jvm['gc']
        self._threads = self.jvm['threads']
        self._buffer_pools = self.jvm['buffer_pools']
        self._classes = self.jvm['classes']

    def __eq__(self, other):
        if not isinstance(other, Metric):
            return NotImplemented

        return self.jvm == other.jvm


class MetricTimestamp(Metric):
    """Metric checking for Elastcsearch nodes

    """

    def __init__(self, metric):
        self.metric = self._is_Metric_instance(metric)
        self.last_checked = datetime.datetime.now()
        self.node_name = self.metric.node_name
        self.heap_used_percent = self.metric.heap_used_percent

    def _time_now(self):
        return datetime.datetime.now()

    def _is_Metric_instance(self, metric):

        if not isinstance(metric, Metric):
            metric = Metric(metric)

        return metric

    def _is_instance(self, new_metric):

        if not isinstance(new_metric, MetricTimestamp):
            new_metric = MetricTimestamp(new_metric)

        return new_metric

    def change_percent(self, new_metric):
        new_metric = self._is_instance(new_metric)

        current = new_metric.heap_used_percent * .01
        previous = self.heap_used_percent * .01

        change_percent = ((float(current) - previous) / previous) * 100

        return change_percent

    def slope(self, new_metric):
        new_metric = self._is_instance(new_metric)

        y1 = self.metric.heap_used_percent
        y2 = new_metric.heap_used_percent

        x1 = self.last_checked.timestamp()
        x2 = new_metric.last_checked.timestamp()

        slope = (y2 - y1) / 1
        # time is currently not taken into account
        # time is disabled
        # slope = (y2 - y1) / (x2 - x1)

        return slope

    def __eq__(self, other):
        if not isinstance(other, MetricTimestamp):
            return NotImplemented

        return self.node_name == other.node_name


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
