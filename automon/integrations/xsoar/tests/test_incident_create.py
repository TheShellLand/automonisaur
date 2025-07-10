import unittest

from automon.integrations.xsoar import XSOARClient

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, ERROR
from automon.helpers import Sleeper

LoggingClient.logging.getLogger('urllib3.connectionpool').setLevel(ERROR)


class MyTestCase(unittest.TestCase):
    client = XSOARClient()

    if client.is_ready():
        def test_auth(self):

            while True:
                incident_type = 'AUTOMON Firewall Rule'

                incident = {
                    'type': incident_type,
                    'createInvestigation': True,
                }

                result = self.client.create_incident(incident)
                pass
                Sleeper.seconds(5)



if __name__ == '__main__':
    unittest.main()
