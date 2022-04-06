import unittest

from automon.integrations.nmap import NmapConfig


class NmapConfigTest(unittest.TestCase):
    def test_config(self):
        self.assertTrue(NmapConfig())


if __name__ == '__main__':
    unittest.main()
