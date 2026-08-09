import unittest

from automon.integrations.youuuuuuutubedl import YoutubeClient


class MyTestCase(unittest.TestCase):
    def test_directories(self):
        c = YoutubeClient()
        self.assertTrue(c.directories.isReady)


if __name__ == '__main__':
    unittest.main()
