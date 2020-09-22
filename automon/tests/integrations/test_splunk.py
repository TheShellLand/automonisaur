import unittest

from automon.integrations.splunk.config import SplunkConfig
from automon.integrations.splunk.client import SplunkClient


class SplunkConfigTest(unittest.TestCase):
    config = SplunkConfig(host='3.236.184.243',
                          port=8089,
                          username='student',
                          password='restC0der',
                          scheme='http')

    def test_init(self):
        self.assertIsNotNone(SplunkConfig())
        self.assertIsNotNone(self.config)

    def test_print(self):
        config = SplunkConfig(host='localhost',
                              port=8089,
                              username='user',
                              password='pass',
                              scheme='http')

        self.assertTrue(f'{self.config}')
        self.assertEqual(f'{config}', f'{config.username}@{config.scheme}://{config.host}:{config.port}')

    def test_info(self):
        config = SplunkConfig(host='localhost',
                              port=8089,
                              username='user',
                              password='pass',
                              scheme='http')

        self.assertTrue(self.config.info())
        self.assertEqual(config.info(), f'{config.username}@{config.scheme}://{config.host}:{config.port}')


class SplunkClientTest(unittest.TestCase):
    config = SplunkConfig(host='3.236.184.243',
                          port=8089,
                          username='student',
                          password='restC0der',
                          scheme='http')

    def test_client_connect_fails(self):
        config = SplunkConfig(host='localhost')
        self.assertFalse(SplunkClient(config).client)

    def test_client_connect(self):
        client = SplunkClient(self.config)
        self.assertIsNotNone(client)
        self.assertTrue(client.client)
        self.assertTrue(client.get_apps())
        self.assertTrue([x.name for x in client.get_apps()])

    def test_init(self):
        self.assertIsNotNone(SplunkClient(self.config))

    def test_jobs(self):
        self.assertTrue(SplunkClient(self.config).get_jobs())
        self.assertTrue(SplunkClient(self.config).job_summary())
        self.assertTrue(SplunkClient(self.config).create_job('test'))


# if __name__ == '__main__':
#     unittest.main()
