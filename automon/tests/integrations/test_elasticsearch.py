import unittest

from automon.integrations.elasticsearch.config import ElasticsearchConfig, SnapshotBot, JVMBot
from automon.integrations.elasticsearch.cleanup import Cleanup


class ElasticsearchTest(unittest.TestCase):

    def test_Cleanup(self):
        self.assertFalse(Cleanup().ping())
        self.assertFalse(Cleanup().get_indices())
        self.assertFalse(Cleanup().search_indices(f''))
        self.assertFalse(Cleanup().delete_indices(f''))

    def test_ElasticsearchConfig(self):
        self.assertTrue(ElasticsearchConfig())

    def test_SnapshotBot(self):
        self.assertTrue(SnapshotBot())

    def test_JVMBot(self):
        self.assertTrue(JVMBot())

# if __name__ == '__main__':
#     unittest.main()
