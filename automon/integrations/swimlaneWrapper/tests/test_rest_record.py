import unittest
import asyncio

from automon.integrations.swimlaneWrapper.client import SwimlaneClientRest

client = SwimlaneClientRest()


class MyTestCase(unittest.TestCase):
    def test_login(self):
        if asyncio.run(client.is_ready()):
            if asyncio.run(client.login()):
                app_id = client.config.appId
                record = asyncio.run(
                    client.record_schema(appId=app_id)
                )

                self.assertTrue(record)

        pass


if __name__ == '__main__':
    unittest.main()
