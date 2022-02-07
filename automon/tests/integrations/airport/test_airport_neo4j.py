import sys
import unittest

from automon.integrations.mac.airport import Airport

from automon.integrations.neo4j import Neo4jClient


class AirportToNeo4jTest(unittest.TestCase):
    a = Airport()
    n = Neo4jClient()

    def test_scan_xml(self):
        if self.a.is_mac:
            self.assertTrue(self.a.scan_xml())
            pass


if __name__ == '__main__':
    unittest.main()
