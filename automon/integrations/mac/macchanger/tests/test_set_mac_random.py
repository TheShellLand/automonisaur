import unittest
import asyncio

from automon import MacChanger

client = MacChanger()


class MacChangerTest(unittest.TestCase):
    if asyncio.run(client.is_ready):
        def test_set_mac_random(self):
            # self.assertTrue(asyncio.run(client.set_mac_random()))
            # self.assertTrue(asyncio.run(client.stdout()))
            # self.assertFalse(asyncio.run(client.stderr()))
            pass


if __name__ == '__main__':
    unittest.main()
