import unittest

from automon.integrations.minioWrapper.config import MinioConfig

c = MinioConfig()


class ConfigTest(unittest.TestCase):

    def test_MinioConfig(self):
        if c.is_ready:
            self.assertTrue(c.is_ready)
        else:
            self.assertFalse(c.is_ready)


if __name__ == '__main__':
    unittest.main()
