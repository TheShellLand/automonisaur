import unittest
import asyncio

from automon.integrations.swimlaneWrapper.client import SwimlaneClientRest

client = SwimlaneClientRest()


class MyTestCase(unittest.TestCase):
    def test_login(self):
        if asyncio.run(client.is_ready()):
            if client.config.jwt_token:
                self.assertTrue(asyncio.run(
                    client.login_token()
                ))

                self.assertFalse(asyncio.run(
                    client.create_auth_token()
                ))

        pass


if __name__ == '__main__':
    unittest.main()
