import unittest
import asyncio

from automon.integrations.swimlaneWrapper.client import SwimlaneClientRest

client = SwimlaneClientRest()


class MyTestCase(unittest.TestCase):
    def test_login(self):
        if asyncio.run(client.is_ready()):
            if asyncio.run(client.login_username_password()):
                self.assertTrue(
                    asyncio.run(client.workspace_list())
                )


if __name__ == '__main__':
    unittest.main()
