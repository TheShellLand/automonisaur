import json

from automon import log
from automon.integrations.requestsWrapper import RequestsClient

from .config import SwimlaneConfig
from .api.v2 import *

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class SwimlaneClient(object):
    pass


class SwimlaneClientRest(object):

    def __init__(self):
        self.config = SwimlaneConfig()
        self.requests = RequestsClient()

        self.auth = None
        self.apps = None
        self.records = None
        self.workspaces = None

    async def is_ready(self):
        if await self.config.is_ready():
            if self.config.headers:
                return True

    async def test_connection(self):
        return

    async def login(self):
        """tries all types of login"""

        if await self.login_username_password():
            return True

        if await self.login_token():
            return True

        return False

    async def login_username_password(self) -> bool:
        """Login with username and password"""
        url = f'{self.host}/{User.login}'

        response = await self.requests.post(
            url=url,
            json=self.config.credentials,
        )

        apiKey = dict(json.loads(self.requests.content)).get('token')
        self.config.apiKey = apiKey

        self.requests.session.headers.update(self.config.headers)

        self.config.userName_model = await self.requests.to_dict()

        return response

    async def login_token(self) -> bool:
        """Login with username and password"""
        url = f'{self.host}/{User.authorize}'

        self.requests.session.headers.update(self.config.headers_jwt_token)

        response = await self.requests.get(
            url=url,
        )

        self.config.userName_model = await self.requests.to_dict()

        return response

    async def create_auth_token(self):
        """Creates a new access token for the user making the request"""
        url = f'{self.host}/{Auth.create}'

        response = await self.requests.post(
            url=url,
        )

        return response

    async def app_list(self):
        url = f'{self.host}/{Application.api}'

        response = await self.requests.get(
            url=url,
        )

        self.apps = await self.requests.to_dict()

        return self.apps

    @property
    def host(self):
        return self.config.host

    async def record_list(self, appId: str):
        url = f'{self.host}/{Record.api(appId)}'

        response = await self.requests.get(
            url=url,
        )

        self.records = await self.requests.to_dict()

        return self.records

    async def record_create(self, appId: str, key: str, value: str or int):
        """create a record"""
        return await self.record_create_easy(appId=appId, key=key, value=value)

    async def record_create_easy(self, appId: str, key: str, value: str or int):
        """create a record with boilerplate added

        The bare minimum you need to send is (assuming application id is 5667113fd273a205bc747cf0):
        {
          "applicationId": "5667113fd273a205bc747cf0",
          "values": {
            "$type": "System.Collections.Generic.Dictionary`2[[System.String, mscorlib],[System.Object, mscorlib]], mscorlib",
            "56674c5cc6c7dea0aeab4aed": "A new value"
          }
        }

        """
        url = f'{self.host}/{Record.api(appId)}'

        record = {
            "applicationId": appId,
            "values": {
                "$type": "System.Collections.Generic.Dictionary`2[[System.String, mscorlib],[System.Object, mscorlib]], mscorlib",
                key: value
            }
        }

        record_json = json.dumps(record)

        response = await self.requests.post(
            url=url,
            json=record
        )

        return response

    async def record_create_hard(self, appId: str, data: dict):
        """create a record the hard way

        no handholding. you're on your own"""
        url = f'{self.host}/{Record.api(appId)}'

        response = await self.requests.post(
            url=url,
            data=data
        )

        return response

    async def record_delete_all(self, appId: str):
        """delete all records in application"""
        url = f'{self.host}/{Record.api(appId)}'

        response = await self.requests.delete(
            url=url
        )

        return response

    async def record_get(self, appId: str, id: str):
        """get a record"""
        url = f'{self.host}/{Record.get(appId=appId, id=id)}'

        response = await self.requests.get(
            url=url
        )

        record = await self.requests.to_dict()

        return record
    async def record_get_base(self, appId: str):
        """get a record"""
        url = f'{self.host}/{Record.api(appId=appId)}'

        response = await self.requests.get(
            url=url
        )

        return response

    @property
    def userId(self):
        return self.config.userName

    async def workspace_list(self):
        url = f'{self.host}/{Workspace.api}'

        response = await self.requests.get(
            url=url,
        )

        self.workspaces = await self.requests.to_dict()

        return self.workspaces
