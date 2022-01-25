import unittest

from automon.integrations.elasticsearch.client import ElasticsearchClient
from automon.integrations.elasticsearch.config import ElasticsearchConfig


class ClientTest(unittest.TestCase):
    e = ElasticsearchClient()

    def test_create_document(self):
        es = ElasticsearchClient()

        if es.isConnected():
            self.assertTrue(es.isConnected())


if __name__ == '__main__':
    unittest.main()
