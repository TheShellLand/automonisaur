import unittest

from automon.integrations.elasticsearch.config import ElasticsearchConfig, SnapshotBot, JVMBot
from automon.integrations.elasticsearch.client import ElasticsearchClient
from automon.integrations.elasticsearch.cleanup import Cleanup
from automon.integrations.elasticsearch.metrics import Metric, MetricTimestamp, Cluster


class Elasticsearch(unittest.TestCase):
    e = ElasticsearchClient()

    def test_create_document(self):
        es = ElasticsearchClient()

        from datetime import datetime

        doc = {
            'timestamp': datetime.now(),
            'yohji': 'yamamoto'

        }

        if self.e.connected():
            self.assertTrue(es.create_document(doc=doc))
            self.assertTrue(es.search_summary())

    def test_ElasticsearchClient(self):
        e = ElasticsearchClient()

        if e.connected():
            self.assertTrue(e)
            self.assertTrue(ElasticsearchClient)
            self.assertTrue(e.ping())
            self.assertTrue(e.get_indices())
            self.assertFalse(e.delete_index(None))
            self.assertFalse(e.search_indices(None))
        else:
            self.assertFalse(e.ping())
            self.assertFalse(e.delete_index(None))
            self.assertFalse(e.search_indices(None))
            self.assertFalse(e.get_indices())

    def test_Cleanup(self):
        if self.e.connected():
            self.assertTrue(Cleanup().get_indices())
            self.assertFalse(Cleanup().search_indices(None))
            # self.assertFalse(Cleanup().delete_indices(None))
        else:
            self.assertFalse(Cleanup().get_indices())
            self.assertFalse(Cleanup().search_indices(None))
            # self.assertFalse(Cleanup().delete_indices(f''))

    def test_ElasticsearchConfig(self):
        self.assertTrue(ElasticsearchConfig())
        self.assertEqual(ElasticsearchConfig(), ElasticsearchConfig())

    def test_SnapshotBot(self):
        self.assertTrue(SnapshotBot())

    def test_JVMBot(self):
        self.assertTrue(JVMBot())

    def test_Cluster(self):
        self.assertTrue(Cluster)

    def test_MetricTimestamp(self):
        # metric = Metric()
        self.assertTrue(MetricTimestamp)
        # self.assertTrue(MetricTimestamp(metric)._time_now())

    def test_Metric(self):
        node = None
        jvm = {
            "timestamp": 1571330469200,
            "uptime_in_millis": 12251148809,
            "mem": {
                "heap_used_in_bytes": 27551308288,
                "heap_used_percent": 82,
                "heap_committed_in_bytes": 33216266240,
                "heap_max_in_bytes": 33216266240,
                "non_heap_used_in_bytes": 162665664,
                "non_heap_committed_in_bytes": 204083200,
                "pools": {
                    "young": {
                        "used_in_bytes": 130099216,
                        "max_in_bytes": 558432256,
                        "peak_used_in_bytes": 558432256,
                        "peak_max_in_bytes": 558432256
                    },
                    "survivor": {
                        "used_in_bytes": 1132144,
                        "max_in_bytes": 69730304,
                        "peak_used_in_bytes": 69730304,
                        "peak_max_in_bytes": 69730304
                    },
                    "old": {
                        "used_in_bytes": 27420076928,
                        "max_in_bytes": 32588103680,
                        "peak_used_in_bytes": 30895029472,
                        "peak_max_in_bytes": 32588103680
                    }
                }
            },
            "threading": {
                "count": 141,
                "peak_count": 223
            },
            "gc": {
                "collectors": {
                    "young": {
                        "collection_count": 533686,
                        "collection_time_in_millis": 37099480
                    },
                    "old": {
                        "collection_count": 75872,
                        "collection_time_in_millis": 9588732
                    }
                }
            },
            "buffer_pools": {
                "mapped": {
                    "count": 7988,
                    "used_in_bytes": 3715149748692,
                    "total_capacity_in_bytes": 3715149748692
                },
                "direct": {
                    "count": 10146,
                    "used_in_bytes": 166764364,
                    "total_capacity_in_bytes": 166764363
                }
            },
            "classes": {
                "current_loaded_count": 17808,
                "total_loaded_count": 18183,
                "total_unloaded_count": 375
            }
        }
        self.assertTrue(Metric)
        self.assertRaises(TypeError, Metric)


if __name__ == '__main__':
    unittest.main()
