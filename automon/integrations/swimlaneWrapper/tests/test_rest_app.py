import unittest
import asyncio
import random

from automon.integrations.swimlaneWrapper.client import SwimlaneClientRest

client = SwimlaneClientRest()


class MyTestCase(unittest.TestCase):
    def test_login(self):
        if asyncio.run(client.is_ready()):
            if asyncio.run(client.login()):
                app_list = asyncio.run(
                    client.app_list())

                self.assertTrue(app_list)

                app = random.choice(app_list)
                appId = app['id']

                app_export = asyncio.run(
                    client.app_export(appId))

                self.assertTrue(app_export)

                app_get = asyncio.run(
                    client.app_by_id(appId=appId))

                self.assertTrue(app_get)

        pass


if __name__ == '__main__':
    unittest.main()
