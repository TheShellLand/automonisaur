import unittest

from automon.integrations.xsoar import XSOARClient

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, ERROR
from automon.helpers import Sleeper

LoggingClient.logging.getLogger('urllib3.connectionpool').setLevel(ERROR)


class MyTestCase(unittest.TestCase):
    client = XSOARClient()

    if client.is_ready():
        def test_auth(self):

            incident_type = None
            type = [incident_type]

            while True:
                incidents_search = self.client.incidents_search(
                    type=type,
                )._incidents_search['data']

                if not incidents_search:
                    break

                incident_ids = [x.id for x in incidents_search if x.type == incident_type]
                # result = self.client.incident_delete(
                #     ids=incident_ids
                # )
                # continue

                for incident in incidents_search:
                    if incident.type == incident_type:
                        result = self.client.incident_delete(
                            id=incident.id,
                        )

                        pass


if __name__ == '__main__':
    unittest.main()
