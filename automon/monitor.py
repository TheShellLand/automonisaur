import os
import json
import requests


class Snapshot:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.id = snapshot['id']
        self.status = snapshot['status']
        self.start_epoch = snapshot['start_epoch']
        self.start_time = snapshot['start_time']
        self.end_epoch = snapshot['end_epoch']
        self.end_time = snapshot['end_time']
        self.duration = snapshot['duration']
        self.indices = snapshot['indices']
        self.successful_shards = snapshot['successful_shards']
        self.failed_shards = snapshot['failed_shards']
        self.total_shards = snapshot['total_shards']

    def __eq__(self, other):
        if not isinstance(other, Snapshot):
            return NotImplemented

        return self.snapshot == other.snapshot


class ElasticsearchSnapshotMonitor():
    def __init__(self, elasticsearch_endpoint, elasticsearch_repository, snapshots_prefix):

        self.endpoint = elasticsearch_endpoint
        self.repository = elasticsearch_repository
        self.snapshots_prefix = snapshots_prefix
        self.snapshots = []
        self.good_snapshots = []
        self.bad_snapshots = []

    def _get_all_snapshots(self, file=None):
        url = '{endpoint}/_cat/snapshots/{repository}?format=json&pretty'.format(
            endpoint=self.endpoint, repository=self.repository)

        if file:
            with open(file, 'rb') as snapshots:
                snapshots = json.load(snapshots)
        else:
            snapshots = requests.get(url).content
            snapshots = json.loads(snapshots)

        for snapshot in snapshots:

            s = Snapshot(snapshot)
            id = s.id
            status = s.status

            if self.snapshots_prefix in id:

                self.snapshots.append(s)

                if status == 'SUCCESS' or status == 'success':
                    self.good_snapshots.append(s)
                else:
                    self.bad_snapshots.append(s)

    def read_file(self, file):
        self._get_all_snapshots(file)

    def check_snapshots(self):
        self._get_all_snapshots()


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
