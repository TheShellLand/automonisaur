import unittest

from automon.integrations.mac import os_is_mac
from automon.integrations.mac.wdutil import WdutilClient


class MyTestCase(unittest.TestCase):
    if WdutilClient().is_ready():
        def test_something(self):
            client = WdutilClient()
            self.assertTrue(client.run('info'))
            self.assertTrue(client.info())
            pass


if __name__ == '__main__':
    unittest.main()
