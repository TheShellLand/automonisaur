import unittest
import asyncio
import sys

from automon.integrations.mac.airport import Airport

airport = Airport()


class AirportTest(unittest.TestCase):

    def test_run(self):
        if asyncio.run(airport.isReady()):
            self.assertTrue(asyncio.run(airport.run()))

    def test_scan(self):
        if asyncio.run(airport.isReady()):
            self.assertTrue(asyncio.run(airport.scan()))
            self.assertTrue(asyncio.run(airport.scan(0)))

    def test_summary(self):
        if asyncio.run(airport.isReady()):
            self.assertTrue(asyncio.run(airport.scan_summary()))
            self.assertTrue(asyncio.run(airport.scan_summary(0)))

    def test_xml(self):
        if asyncio.run(airport.isReady()):
            scan = asyncio.run(airport.scan_xml())
            if scan:
                self.assertTrue(scan)
            self.assertFalse(asyncio.run(airport.scan_xml(0)))

    def test_set_channel(self):
        if asyncio.run(airport.isReady()):
            pass
            # self.assertTrue(a.set_channel(10))

    def test_disassociate(self):
        if asyncio.run(airport.isReady()):
            pass
            # self.assertTrue(a.disassociate())

    def test_getinto(self):
        if asyncio.run(airport.isReady()):
            self.assertTrue(asyncio.run(airport.getinfo()))

    def test_create_psk(self):
        if asyncio.run(airport.isReady()):
            self.assertTrue(asyncio.run(airport.create_psk(ssid='AAAAAAAA', passphrase='CALVIN')))


if __name__ == '__main__':
    unittest.main()
