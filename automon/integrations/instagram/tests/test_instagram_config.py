import unittest

from ..config import InstagramConfig

config = InstagramConfig()


class InstagramConfigTest(unittest.TestCase):
    def test_config(self):
        if config.is_configured:
            self.assertTrue(config.is_configured)


if __name__ == '__main__':
    unittest.main()
