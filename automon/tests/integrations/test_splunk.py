import unittest

from automon.integrations.splunk.config import SplunkConfig
from automon.integrations.splunk.client import SplunkClient

config_mock = SplunkConfig(
    host='localhost',
    port=8089,
    username='user',
    password='pass',
    scheme='http')

config_cloud = SplunkConfig(
    host='splunkcloud.com',
    port=8089,
    username='user',
    password='pass',
    scheme='http')


class SplunkConfigTest(unittest.TestCase):

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

    def test_client_connect_fails(self):
        config = SplunkConfig(host='localhost')
        self.assertFalse(SplunkClient(config).client)

    def test_client_connect(self):
        client = SplunkClient(config_cloud)
        self.assertIsNotNone(client)
        self.assertIsNotNone(client.client)
        self.assertTrue(client.get_apps())
        self.assertTrue([x.name for x in client.get_apps()])

    def test_init(self):
        self.assertIsNotNone(SplunkClient(config_cloud))

    def test_jobs(self):
        self.assertTrue(SplunkClient(config_cloud).jobs())
        self.assertTrue(SplunkClient(config_cloud).job_summary())
        self.assertTrue(SplunkClient(config_cloud).create_job('search * '))

    def test_search(self):
        self.assertTrue(SplunkClient(config_cloud).search('search index=* | head 10'))

    def test_oneshot(self):
        self.assertIsNotNone(SplunkClient(config_cloud).oneshot('search * | head 10'))

# if __name__ == '__main__':
#     unittest.main()
