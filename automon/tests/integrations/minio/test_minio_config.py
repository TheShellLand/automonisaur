import unittest

from automon.integrations.minio.config import MinioConfig


class ConfigTest(unittest.TestCase):
    def test_MinioConfig(self):
        self.assertTrue(MinioConfig())


if __name__ == '__main__':
    unittest.main()
