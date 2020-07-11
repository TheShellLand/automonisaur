import unittest

from automon.integrations.elasticsearch import ElasticsearchConnect
from automon.integrations.elasticsearch.config import ConfigESJVMBot
from automon.integrations.elasticsearch.config import ConfigESSnapshotBot


class ElasticsearchTest(unittest.TestCase):

    def test_ElasticsearchConnect(self):
        self.assertFalse(
            ElasticsearchConnect(
                'elasticsearch.0000000', use_ssl=False, request_timeout=1).eswrapper.ping())

    def test_ConfigESSnapshotBot(self):
        self.assertTrue(ConfigESSnapshotBot())

    def test_ConfigESJVMBot(self):
        self.assertTrue(ConfigESJVMBot())

# if __name__ == '__main__':
#     unittest.main()
