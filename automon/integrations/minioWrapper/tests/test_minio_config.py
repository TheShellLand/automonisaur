import unittest

from automon.integrations.minioWrapper.config import MinioConfig

c = MinioConfig()


class ConfigTest(unittest.TestCase):

    def test_MinioConfig(self):
        if c.is_ready():
            self.assertTrue(MinioConfig().is_ready())
        else:
            self.assertFalse(MinioConfig().is_ready())


if __name__ == '__main__':
    unittest.main()
