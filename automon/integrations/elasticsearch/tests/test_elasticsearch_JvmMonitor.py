import unittest

from automon.integrations.elasticsearch.jvm import ElasticsearchJvmMonitor
from automon.integrations.elasticsearch.client import ElasticsearchClient


class ElasticsearchJvmMonitorTest(unittest.TestCase):

    def test_ElasticsearchJvmMonitor(self):
        self.assertTrue(ElasticsearchJvmMonitor)
        self.assertTrue(ElasticsearchJvmMonitor())
        self.assertFalse(ElasticsearchJvmMonitor().get_metrics())
        # self.assertFalse(ElasticsearchJvmMonitor().read_file())


if __name__ == '__main__':
    unittest.main()
