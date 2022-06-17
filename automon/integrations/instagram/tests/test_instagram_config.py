import unittest

from ..config import InstagramConfig

config = InstagramConfig()


class InstagramConfigTest(unittest.TestCase):
    def test_config(self):
        if config.login and config.password:
            self.assertTrue(config.isConfigured())


if __name__ == '__main__':
    unittest.main()
