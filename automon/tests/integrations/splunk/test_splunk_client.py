import unittest

from automon.integrations.splunk import SplunkClient

cloud = SplunkClient()


class SplunkClientTest(unittest.TestCase):

    def test_client_connect(self):
        if cloud.is_connected():
            self.assertIsNotNone(cloud)
            self.assertIsNotNone(cloud.client)
            self.assertTrue(cloud.get_apps())
            self.assertTrue([x.name for x in cloud.get_apps()])

    def test_init(self):
        self.assertIsNotNone(SplunkClientTest())

    def test_jobs(self):
        if cloud.is_connected():
            self.assertTrue(cloud.jobs())
            self.assertTrue(cloud.job_summary())
            self.assertTrue(cloud.create_job('search * '))

    def test_search(self):
        if cloud.is_connected():
            self.assertTrue(cloud.search('search index=* | head 10'))

    def test_oneshot(self):
        if cloud.is_connected():
            self.assertIsNotNone(cloud.oneshot('search * | head 10'))


if __name__ == '__main__':
    unittest.main()
