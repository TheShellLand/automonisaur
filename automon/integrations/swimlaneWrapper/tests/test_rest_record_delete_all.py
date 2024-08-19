import unittest
import asyncio

from automon.integrations.swimlaneWrapper.client import SwimlaneClientRest

client = SwimlaneClientRest()


class MyTestCase(unittest.TestCase):
    def test_record_delete_all(self):
        if asyncio.run(client.is_ready()):
            if asyncio.run(client.login()):
                app_id = client.config.appId
                delete_all = asyncio.run(
                    client.record_delete_all(appId=app_id)
                )

                self.assertTrue(delete_all)

        pass


if __name__ == '__main__':
    unittest.main()
