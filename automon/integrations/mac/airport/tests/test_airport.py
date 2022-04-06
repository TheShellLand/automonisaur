import sys
import unittest

from automon.integrations.mac.airport import Airport


class AirportTest(unittest.TestCase):
    a = Airport()

    def test_run(self):
        if self.a.isReady():
            self.assertTrue(self.a.run())

    def test_scan(self):
        if self.a.isReady():
            self.assertTrue(self.a.scan())
            self.assertTrue(self.a.scan(0))

    def test_summary(self):
        if self.a.isReady():
            self.assertTrue(self.a.scan_summary())
            self.assertTrue(self.a.scan_summary(0))

    def test_xml(self):
        if self.a.isReady():
            scan = self.a.scan_xml()
            if scan:
                self.assertTrue(scan)
            self.assertFalse(self.a.scan_xml(0))

    def test_set_channel(self):
        if self.a.isReady():
            pass
            # self.assertTrue(self.a.set_channel(10))

    def test_disassociate(self):
        if self.a.isReady():
            pass
            # self.assertTrue(self.a.disassociate())

    def test_getinto(self):
        if self.a.isReady():
            self.assertTrue(self.a.getinfo())

    def test_create_psk(self):
        if self.a.isReady():
            self.assertTrue(self.a.create_psk(ssid='AAAAAAAA', passphrase='CALVIN'))


if __name__ == '__main__':
    unittest.main()
