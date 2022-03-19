import os.path
import functools

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from automon.log import Logging

from .urls import PeopleUrls
from .config import PeopleConfig
from .results import ConnectionsResults

log = Logging(name='PeopleClient', level=Logging.DEBUG)


class PeopleClient:
    def __init__(self, client_id: str = None,
                 client_secret: str = None,
                 config: PeopleConfig = None):
        """Google People API Client"""

        self.config = config or PeopleConfig(
            client_id=client_id,
            client_secret=client_secret
        )

        self.contacts = []

    def __repr__(self):
        return f'{self.__dict__}'

    @property
    def _build(self) -> build:
        return build('people', 'v1', credentials=self.config.Credentials)

    @property
    def _client_config(self) -> dict:
        return self.config.oauth_dict()

    @property
    def _connections(self, *args, **kwargs):
        return self._people.connections(*args, **kwargs)

    @property
    def _people(self, *args, **kwargs):
        return self._build.people(*args, **kwargs)

    def _execute(self, func) -> ConnectionsResults:
        if self.isConnected():
            result = func.execute()
            return ConnectionsResults(result)

    def _list(self, *args, **kwargs) -> ConnectionsResults:
        return self._execute(
            self._connections.list(*args, **kwargs)
        )

    @property
    def client(self) -> build:
        return self._build

    def authenticate(self) -> bool:
        """Get Oauth"""
        if not self.config.isReady():
            return False

        creds = self.config.Credentials
        client_config = self._client_config
        scopes = self.config.scopes

        refresh_token = creds.refresh_token

        if refresh_token:
            try:
                creds.refresh(Request())
                return True
            except Exception as e:
                log.error(msg=f'authentication failed {e}', raise_exception=False)

        else:
            flow = InstalledAppFlow.from_client_config(
                client_config,
                scopes
            )
            new_creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            self.config.load_token(new_creds)
            return True

        return False

    def isConnected(self) -> bool:
        """Check if authenticated to make requests"""
        return self.authenticate()

    def _isConnected(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.authenticate():
                return func(self, *args, **kwargs)

        return wrapped

    @_isConnected
    def list_connections(
            self,
            resourceName: str = None,
            pageToken: str = None,
            pageSize: int = 2000,
            sortOrder: str = None,
            requestSyncToken: bool = None,
            syncToken: str = None,
            personFields: str = None,
            sources: str = None,
            **kwargs) -> ConnectionsResults:
        """

        :param resourceName: Required. The resource name to return connections for. Only people/me is valid
        :param pageToken:
        :param pageSize:
        :param sortOrder:
        :param requestSyncToken:
        :param syncToken:
        :param personFields:
        :param sources:
        :param args:
        :param kwargs:
        :return: PeopleResults
        """

        if not resourceName:
            resourceName = PeopleUrls().resourceName()

        if not personFields:
            personFields = PeopleUrls().personFields_toStr()

        return self._list(
            resourceName=resourceName,
            pageToken=pageToken,
            pageSize=pageSize,
            sortOrder=sortOrder,
            requestSyncToken=requestSyncToken,
            syncToken=syncToken,
            sources=sources,
            personFields=personFields,
            **kwargs)

    @_isConnected
    def list_connection_generator(self, pageToken: str = None, **kwargs):
        """Generator for paging through connections"""

        while True:
            result = self.list_connections(pageToken=pageToken, **kwargs)
            yield result
            pageToken = result.nextPageToken

            if not pageToken:
                break
