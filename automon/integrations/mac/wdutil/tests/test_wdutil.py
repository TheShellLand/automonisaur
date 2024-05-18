import unittest

from automon import os_is_mac
from automon.integrations.mac.wdutil import WdutilClient


class MyTestCase(unittest.TestCase):

    if os_is_mac():
        def test_something(self):
            self.assertTrue(WdutilClient().wdutil)


if __name__ == '__main__':
    unittest.main()
