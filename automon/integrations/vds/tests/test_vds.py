import unittest

from automon.integrations.vds.client import VdsRestClient
from automon.integrations.vds.config import VdsConfig


class VdsTest(unittest.TestCase):
    def test_VdsConfig(self):
        self.assertTrue(VdsRestClient())

    def test_VdsClient(self):
        self.assertTrue(VdsConfig())


if __name__ == '__main__':
    unittest.main()
