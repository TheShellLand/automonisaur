import unittest

from automon.integrations.minio.client import MinioClient
from automon.integrations.minio.config import MinioConfig


class MinioTest(unittest.TestCase):
    def test_MinioConfig(self):
        self.assertTrue(MinioConfig())

    def test_MinioClient(self):
        self.assertTrue(MinioClient())


if __name__ == '__main__':
    unittest.main()
