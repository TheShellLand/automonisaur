import unittest

from automon.integrations.shodan import Shodan, ShodanConfig


class ShodanTest(unittest.TestCase):
    def test_Shodan(self):
        self.assertTrue(Shodan())
        self.assertTrue(Shodan().request())

    def test_ShodanConfig(self):
        self.assertTrue(ShodanConfig())


if __name__ == '__main__':
    unittest.main()
