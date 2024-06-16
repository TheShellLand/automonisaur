import unittest

from automon.integrations.mac import os_is_mac
from automon.integrations.mac.wdutil import WdutilClient, WdutilConfig


class MyTestCase(unittest.TestCase):
    if os_is_mac():
        if WdutilConfig().is_ready():

            def test_something(self):
                self.assertTrue(
                    WdutilClient().is_ready()
                )


if __name__ == '__main__':
    unittest.main()
