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
            playbookId = None
            createInvestigation = True

            while True:
                result = self.client.incident_create(
                    type=incident_type,
                    name='Run Playbook',
                    playbookId=playbookId,
                    createInvestigation=createInvestigation,
                )._incident_created
                print(f'{self.client.config.host}/#/WorkPlan/{result.id}')

                Sleeper.seconds(5)
                pass


if __name__ == '__main__':
    unittest.main()
