import unittest

from ..true_or_false import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertTrue(is_true('true'))
        self.assertFalse(is_true('false'))
        self.assertTrue(is_false('false'))
        self.assertFalse(is_false('true'))


if __name__ == '__main__':
    unittest.main()
