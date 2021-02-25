import sys
import unittest

from automon.integrations.mac.airport.scanner import Airport


class AirportTest(unittest.TestCase):
    a = Airport()

    def test_Airport(self):
        if sys.platform == 'darwin':
            self.assertTrue(self.a.run())
            self.assertTrue(self.a.scan())
            self.assertTrue(self.a.scan(0))
            self.assertTrue(self.a.scan_summary())
            self.assertTrue(self.a.scan_summary(0))
            self.assertTrue(self.a.scan_xml())
            self.assertTrue(self.a.scan_xml(0))

            # self.assertTrue(self.a.set_channel(10))
            # self.assertTrue(self.a.disassociate())

            self.assertTrue(self.a.getinfo())
            self.assertTrue(self.a.create_psk(ssid='AAAAAAAA', passphrase='CALVIN'))


if __name__ == '__main__':
    unittest.main()
