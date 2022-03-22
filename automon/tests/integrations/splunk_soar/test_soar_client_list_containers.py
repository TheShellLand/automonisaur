import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):

    # def test_list_containers(self):
    #     if c.isConnected():
    #         self.assertTrue(c.list_containers())
    #     else:
    #         self.assertFalse(c.list_containers())

    def test_list_containers_generator(self):
        if c.isConnected():
            containers = [x for x in c.list_containers_generator(page_size=100, max_pages=2)]
            self.assertTrue(containers)
        else:
            self.assertFalse(c.list_containers_generator())


if __name__ == '__main__':
    unittest.main()
