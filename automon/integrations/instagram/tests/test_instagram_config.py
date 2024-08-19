import unittest

from ..config import InstagramConfig

config = InstagramConfig()


class InstagramConfigTest(unittest.TestCase):
    def test_config(self):
        if config.is_ready():
            self.assertTrue(config.is_ready())


if __name__ == '__main__':
    unittest.main()
