import unittest

from automon.integrations.mac import os_is_mac
from automon.integrations.mac.wdutil import WdutilConfig


class MyTestCase(unittest.TestCase):
    if os_is_mac():
        def test_something(self):
            self.assertFalse(WdutilConfig().is_ready())


if __name__ == '__main__':
    unittest.main()
