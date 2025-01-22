import unittest
import sys

from automon.integrations.mac.airport import Airport

airport = Airport()


class AirportTest(unittest.TestCase):

    def test_run(self):
        if airport.isReady():
            self.assertTrue(airport.run())

    def test_scan(self):
        if airport.isReady():
            self.assertTrue(airport.scan())
            self.assertTrue(airport.scan(0))

    def test_summary(self):
        if airport.isReady():
            self.assertTrue(airport.scan_summary())
            self.assertTrue(airport.scan_summary(0))

    def test_xml(self):
        if airport.isReady():
            scan = airport.scan_xml()
            if scan:
                self.assertTrue(scan)
            self.assertFalse(airport.scan_xml(0))

    def test_set_channel(self):
        if airport.isReady():
            pass
            # self.assertTrue(a.set_channel(10)

    def test_disassociate(self):
        if airport.isReady():
            pass
            # self.assertTrue(a.disassociate()

    def test_getinto(self):
        if airport.isReady():
            self.assertTrue(airport.getinfo())

    def test_create_psk(self):
        if airport.isReady():
            self.assertTrue(airport.create_psk(ssid='AAAAAAAA', passphrase='CALVIN'))


if __name__ == '__main__':
    unittest.main()
