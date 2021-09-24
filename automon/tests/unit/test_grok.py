import unittest

from automon.helpers.grok import Grok, GrokLegacy


class GrokTest(unittest.TestCase):

    def test_Grok(self):
        self.assertTrue(Grok())


class GrokLegacyTest(unittest.TestCase):

    def test_GrokLegacy(self):
        self.assertTrue(GrokLegacy())


if __name__ == '__main__':
    unittest.main()
