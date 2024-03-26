import unittest

from automon.helpers.grok import Grok


class GrokTest(unittest.TestCase):

    def test_Grok(self):
        self.assertTrue(Grok())


if __name__ == '__main__':
    unittest.main()
