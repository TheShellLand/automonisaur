import unittest

from automon.log import log_secret


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(log_secret(secret='password'), '********************************')  # add assertion here


if __name__ == '__main__':
    unittest.main()
