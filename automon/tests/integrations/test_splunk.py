import unittest

from automon.integrations.splunk.config import SplunkConfig
from automon.integrations.splunk.client import SplunkClient

config_mock = SplunkConfig(
    host='localhost',
    username='user',
    password='pass')

config_cloud = SplunkConfig(
    host='splunkcloud.com',
    username='user',
    password='pass')

mock = SplunkClient(config_mock)
cloud = SplunkClient(config_cloud)


class SplunkConfigTest(unittest.TestCase):
    config = SplunkConfig()

    def test_init(self):
        self.assertIsNotNone(SplunkConfig())
        self.assertIsNotNone(self.config)

    def test_print(self):
        self.assertTrue(f'{self.config}')
        self.assertEqual(f'{config_mock}',
                         f'{config_mock.username}@{config_mock.scheme}://{config_mock.host}:{config_mock.port}')

    def test_info(self):
        self.assertTrue(self.config.info())
        self.assertEqual(config_mock.info(),
                         f'{config_mock.username}@{config_mock.scheme}://{config_mock.host}:{config_mock.port}')


class SplunkClientTest(unittest.TestCase):

    def test_client_connect(self):
        if cloud.connected:
            self.assertIsNotNone(cloud)
            self.assertIsNotNone(cloud.client)
            self.assertTrue(cloud.get_apps())
            self.assertTrue([x.name for x in cloud.get_apps()])

    def test_init(self):
        self.assertIsNotNone(SplunkClientTest())

    def test_jobs(self):
        if cloud.connected:
            self.assertTrue(cloud.jobs())
            self.assertTrue(cloud.job_summary())
            self.assertTrue(cloud.create_job('search * '))

    def test_search(self):
        if cloud.connected:
            self.assertTrue(cloud.search('search index=* | head 10'))

    def test_oneshot(self):
        if cloud.connected:
            self.assertIsNotNone(cloud.oneshot('search * | head 10'))


if __name__ == '__main__':
    unittest.main()
