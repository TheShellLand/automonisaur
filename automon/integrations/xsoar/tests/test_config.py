import unittest

from automon.integrations.xsoar import XSOARConfig


class MyTestCase(unittest.TestCase):
    test = XSOARConfig()

    if test.is_ready():
        def test_config(self):
            self.assertTrue(self.test.is_ready())


if __name__ == '__main__':
    unittest.main()
