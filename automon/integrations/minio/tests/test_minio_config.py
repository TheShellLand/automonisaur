import unittest

from automon.integrations.minio.config import MinioConfig

c = MinioConfig()


class ConfigTest(unittest.TestCase):

    def test_MinioConfig(self):
        if c.isReady():
            self.assertTrue(MinioConfig().isReady())
        else:
            self.assertFalse(MinioConfig().isReady())


if __name__ == '__main__':
    unittest.main()
