import unittest

from automon.integrations.elasticsearch.client import ElasticsearchClient


class Elasticsearch(unittest.TestCase):

    def test_endpoints(self):
        c = ElasticsearchClient()

        if c.connected():
            self.assertTrue(c)
            self.assertTrue(c.get_indices())
            self.assertTrue(c.info())
            self.assertTrue(c.ping())


if __name__ == '__main__':
    unittest.main()
