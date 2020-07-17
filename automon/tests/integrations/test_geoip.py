import unittest

from automon.integrations.geoip import Geoip


class GeoipTest(unittest.TestCase):
    def test_Geoip(self):
        self.assertTrue(Geoip('10.0.0.1'))
        self.assertIsNone(Geoip('10.0.0.1').geoiptool())

# if __name__ == '__main__':
#     unittest.main()
