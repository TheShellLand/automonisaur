import unittest
import asyncio
import random

from automon.integrations.swimlaneWrapper.client import SwimlaneClientRest

client = SwimlaneClientRest()


class MyTestCase(unittest.TestCase):
    def test_login(self):
        if asyncio.run(client.is_ready()):
            if asyncio.run(client.login_token()):
                logs = asyncio.run(
                    client.logging_recent())

                jobId = '6602057d6158e302aff869b2'

                logs_job = asyncio.run(
                    client.logging_by_id(jobId=jobId))


        pass


if __name__ == '__main__':
    unittest.main()
