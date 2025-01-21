import unittest

from automon.integrations.xsoar import XSOARClient


class MyTestCase(unittest.TestCase):
    test = XSOARClient()

    if test.is_ready():
        def test_auth(self):
            result = self.test.reports()
            pass


if __name__ == '__main__':
    unittest.main()
