import unittest

from automon.integrations.splunk import SplunkConfig

config_mock = SplunkConfig(
    host='localhost',
    username='user',
    password='pass')

config_cloud = SplunkConfig(
    host='splunkcloud.com',
    username='user',
    password='pass')


class SplunkConfigTest(unittest.TestCase):
    config = SplunkConfig()

    def test_init(self):
        self.assertIsNotNone(SplunkConfig())

    def test_print(self):
        self.assertTrue(f'{self.config}')

    def test_info(self):
        self.assertTrue(self.config.info())


if __name__ == '__main__':
    unittest.main()
