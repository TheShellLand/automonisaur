import sys
import unittest

from automon.integrations.mac.airport import Airport

from automon.integrations.neo4j import Neo4jClient


class AirportToNeo4jTest(unittest.TestCase):
    a = Airport()
    n = Neo4jClient()

    def test_scan_xml(self):
        if self.a.isReady():
            test = self.a.scan_xml()
            if test:
                self.assertTrue(test)

        if self.n.isConnected():
            # self.n.delete_all()
            for bssid in self.a.ssids:
                flatten = bssid._ssid
                flatten.update(bssid.__dict__)
                flatten.pop('_ssid')

                self.assertTrue(self.n.merge_dict(
                    prop='BSSID',
                    value=bssid.BSSID,
                    data=flatten,
                    label='BSSID',
                ))

                self.assertTrue(self.n.relationship(
                    A_prop='SSID', A_value=bssid.SSID,
                    B_prop='SSID', B_value=bssid.SSID,
                    WHERE=f'A.BSSID <> B.BSSID', label='EXTENDS'
                ))


if __name__ == '__main__':
    unittest.main()
