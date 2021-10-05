import unittest

from automon.helpers.regex import *


class RegexTest(unittest.TestCase):

    def test_magic(self):
        self.assertTrue(Magic)
        test = '100.15.96.234 helehleeajd'
        self.assertTrue(Magic.magic_box(test))

    def test_geolocation(self):
        self.assertTrue(geolocation)


if __name__ == '__main__':
    unittest.main()
