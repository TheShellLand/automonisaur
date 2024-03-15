import unittest
import json
import asyncio

from automon.integrations.swimlaneWrapper.client import SwimlaneClientRest

client = SwimlaneClientRest()


class MyTestCase(unittest.TestCase):
    def test_login(self):
        if asyncio.run(client.is_ready()):
            if asyncio.run(client.login_token()):
                self.assertTrue(asyncio.run(
                    client.app_list()
                ))

                key = 'a7m4r'       # json
                value = json.dumps(dict(
                    key='value',
                    key2='value2',
                ))

                record_new = asyncio.run(
                    client.record_create(
                        appId=client.config.appId,
                        key=key,
                        value=value)
                )

                self.assertTrue(record_new)

                record_id = record_new.get('id')

                record_get = asyncio.run(
                    client.record_get(appId=client.config.appId, id=record_id))

                self.assertTrue(record_get)

                pass


if __name__ == '__main__':
    unittest.main()
