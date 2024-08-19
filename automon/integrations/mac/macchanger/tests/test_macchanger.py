import unittest
import asyncio

from automon.integrations.mac import MacChanger

client = MacChanger()


class MacChangerTest(unittest.TestCase):
    if asyncio.run(client.is_ready):
        def test_random_mac(self):
            self.assertTrue(asyncio.run(client.random_mac()))

        def test_ifconfig(self):
            self.assertTrue(asyncio.run(client.ifconfig()))
            self.assertTrue(asyncio.run(client.stdout()))
            self.assertFalse(asyncio.run(client.stderr()))


if __name__ == '__main__':
    unittest.main()
