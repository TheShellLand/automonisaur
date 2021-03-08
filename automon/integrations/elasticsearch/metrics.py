import datetime


class Cluster(dict):
    def __init__(self, raw_metrics: dict):
        self._all_metrics = raw_metrics
        self._nodes = {
            'total': self._all_metrics.get('_nodes').get('total'),
            'successful': self._all_metrics.get('_nodes').get('successful'),
            'failed': self._all_metrics.get('_nodes').get('failed')
        }

        self.cluster_name = self._all_metrics.get('cluster_name')
        self.nodes = []
        self.metrics = []

        for node in self._all_metrics.get('nodes').items():
            self.nodes.append(node[1])

        for metric in self.nodes:
            self.metrics.append(Metric(metric))


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
        "threading" : {
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

    def __init__(self, node: Cluster):
        self._node = node
        self.node_name = self._node['name']

        self.jvm = self._node.get('jvm')
        self.heap_used_percent = self.jvm.get('mem').get('heap_used_percent')

        self._mem = self.jvm.get('mem')
        self._timestamp = self.jvm.get('timestamp')
        self._uptime_in_millis = self.jvm.get('uptime_in_millis')
        self._gc = self.jvm.get('gc')
        self._threads = self.jvm.get('threading')
        self._buffer_pools = self.jvm.get('buffer_pools')
        self._classes = self.jvm.get('classes')

    def __eq__(self, other):
        if not isinstance(other, Metric):
            return NotImplemented

        return self.jvm == other.jvm


class MetricTimestamp(Metric):
    """Metric checking for Elastcsearch nodes"""

    def __init__(self, metric: Metric):
        self.metric = metric if isinstance(metric, Metric) else Metric(metric)
        self.last_checked = datetime.datetime.now()
        self.node_name = self.metric.node_name
        self.heap_used_percent = self.metric.heap_used_percent

    @staticmethod
    def _time_now():
        return datetime.datetime.now()

    @staticmethod
    def _is_instance(new_metric):

        if not isinstance(new_metric, MetricTimestamp):
            new_metric = MetricTimestamp(new_metric)

        return new_metric

    def change_percent(self, new_metric):
        current = self._is_instance(new_metric).heap_used_percent * .01
        previous = self.heap_used_percent * .01

        return ((float(current) - previous) / previous) * 100

    # def slope(self, new_metric):
    #     new_metric = self._is_instance(new_metric)
    #
    #     y1 = self.metric.heap_used_percent
    #     y2 = new_metric.heap_used_percent
    #
    #     x1 = self.last_checked.timestamp()
    #     x2 = new_metric.last_checked.timestamp()
    #
    #     slope = (y2 - y1) / 1
    #     # time is currently not taken into account
    #     # time is disabled
    #     # slope = (y2 - y1) / (x2 - x1)
    #
    #     return slope

    def __eq__(self, other):
        if not isinstance(other, MetricTimestamp):
            return NotImplemented

        return self.node_name == other.node_name
