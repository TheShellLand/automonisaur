import unittest

from automon.integrations.minio.config import MinioConfig


class Config(unittest.TestCase):
    def test_MinioConfig(self):
        self.assertTrue(MinioConfig())


if __name__ == '__main__':
    unittest.main()
