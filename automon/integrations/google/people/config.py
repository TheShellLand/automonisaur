import json
import os.path
import datetime

from io import StringIO, BytesIO

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from automon.log import Logging
from automon.helpers import environ

log = Logging(name='PeopleConfig', level=Logging.DEBUG)


class PeopleConfig:

    def __init__(self,
                 token=None,
                 refresh_token=None,
                 id_token=None,
                 token_uri=None,
                 client_id=None,
                 client_secret=None,
                 scopes=None,
                 default_scopes=None,
                 quota_project_id=None,
                 expiry=None,
                 rapt_token=None,
                 refresh_handler=None,
                 enable_reauth_refresh=False,
                 auth_uri=None,
                 auth_provider_x509_cert_url=None,
                 redirect_uris=None,
                 client_type=None
                 ):
        """Google People API config"""

        self._token = token
        self._refresh_token = refresh_token
        self._id_token = id_token
        self._token_uri = token_uri
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = scopes
        self._default_scopes = default_scopes
        self._quota_project_id = quota_project_id
        self._expiry = expiry
        self._rapt_token = rapt_token
        self._refresh_handler = refresh_handler
        self._enable_reauth_refresh = enable_reauth_refresh
        self._redirect_uris = redirect_uris

        self._auth_uri = auth_uri
        self._auth_provider_x509_cert_url = auth_provider_x509_cert_url

        self._client_type = client_type

    def __repr__(self):
        return f'{self.__dict__}'

    @property
    def auth_uri(self) -> str:
        return self._auth_uri or environ(
            'GOOGLE_AUTH_URI',
            'https://accounts.google.com/o/oauth2/auth'
        )

    @property
    def auth_provider_x509_cert_url(self) -> str:
        return self._auth_provider_x509_cert_url or environ(
            'GOOGLE_CERT_URL',
            'https://www.googleapis.com/oauth2/v1/certs'
        )

    @property
    def client_id(self) -> str:
        return self._client_id or environ('GOOGLE_CLIENT_ID')

    @property
    def client_secret(self) -> str:
        return self._client_secret or environ('GOOGLE_CLIENT_SECRET')

    @property
    def client_type(self) -> str:

        if self._client_type:
            return self._client_type

        if environ('GOOGLE_OAUTH_WEB'):
            return 'web'

        if environ('GOOGLE_OAUTH_DESKTOP'):
            return 'installed'

        return self._client_type

    @property
    def default_scopes(self) -> list:
        return self._default_scopes

    @property
    def enable_reauth_refresh(self) -> bool:
        return self._enable_reauth_refresh

    @property
    def expiry(self) -> datetime:
        return self._expiry

    @property
    def Credentials(self) -> Credentials:
        return Credentials(
            token=self.token,
            refresh_token=self.refresh_token,
            id_token=self.id_token,
            token_uri=self.token_uri,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.scopes,
            default_scopes=self.default_scopes,
            quota_project_id=self._quota_project_id,
            expiry=self.expiry,
            rapt_token=self.rapt_token,
            refresh_handler=self.refresh_handler,
            enable_reauth_refresh=self.enable_reauth_refresh,
        )

    @property
    def id_token(self) -> str:
        return self._id_token

    @property
    def quota_project_id(self) -> str:
        return self._quota_project_id or environ('GOOGLE_PROJECT_ID')

    @property
    def redirect_uris(self) -> list:
        return self._redirect_uris

    @property
    def refresh_handler(self) -> str:
        return self._refresh_handler

    @property
    def rapt_token(self) -> str:
        return self._rapt_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token or environ('GOOGLE_REFRESH_TOKEN')

    @property
    def scopes(self) -> list:
        return self._scopes or ['https://www.googleapis.com/auth/contacts.readonly']

    @property
    def token(self) -> str:
        return self._token or environ('GOOGLE_TOKEN')

    @property
    def token_uri(self) -> str:
        return self._token_uri or environ(
            'GOOGLE_TOKEN_URI',
            'https://oauth2.googleapis.com/token'
        )

    def credentials_file(self) -> StringIO:
        return StringIO(f'{self.Credentials.to_json()}')

    def credentials_json(self) -> str:
        return self.Credentials.to_json()

    def credentials_dict(self) -> dict:
        return json.loads(self.Credentials.to_json())

    def oauth_dict(self) -> dict:
        """Oauth credentials"""
        if self.client_type:
            return {
                f'{self.client_type}': dict(
                    client_id=self.client_id,
                    project_id=self.quota_project_id,
                    auth_uri=self.auth_uri,
                    token_uri=self.token_uri,
                    auth_provider_x509_cert_url=self.auth_provider_x509_cert_url,
                    client_secret=self.client_secret,
                    redirect_uris=self.redirect_uris
                )
            }

        log.warn(f'Missing client_type')
        return False

    def from_authorized_user_file(self, file: str) -> Credentials:
        """Load token.json"""
        return self.Credentials.from_authorized_user_file(file, self.scopes)

    def isReady(self):
        if self.client_type:
            return True
        if self.oauth_dict():
            return True

        log.warn(f'config is not ready')
        return False

    def load_oauth(self, oauth: dict) -> Credentials:
        if 'installed' in oauth.keys():
            oauth = oauth['installed']
            self._client_type = 'installed'
            return self.update(oauth)

        if 'web' in oauth.keys():
            oauth = oauth['web']
            self._client_type = 'web'
            return self.update(oauth)

        else:
            log.error(msg=f'Unsupported or not an Oauth token. {oauth}', raise_exception=True)

        return self.Credentials

    def load_oauth_file(self, file: str) -> Credentials:
        """Load Oauth credentials.json"""
        with open(file, 'r') as f:
            creds = dict(json.loads(f.read()))
        return self.load_oauth(creds)

    def load_token(self, token: Credentials) -> Credentials:
        return self.update(token.__dict__)

    def load_token_json(self, token: str) -> Credentials:
        token_dict = json.loads(token)
        return self.update(token_dict)

    def update(self, creds: dict) -> Credentials:
        """Update properties"""
        for k, v in creds.items():
            if k[0] == '_':
                k = k
            else:
                k = f'_{k}'
            self.__dict__[k] = v
        return self.Credentials
