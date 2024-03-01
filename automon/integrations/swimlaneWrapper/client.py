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
        url = f'{self.host}/{User.login}'

        self.requests.session.headers.update(self.config.headers)

        response = await self.requests.post(
            url=url,
        )

        return response

    async def create_auth_token(self):
        """Creates a new access token for the user making the request"""
        url = f'{self.host}/{Auth(userId=self.userId).create}'

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