import os
import json
import base64
import pickle

import google.oauth2.credentials
import google.oauth2.service_account
import google.auth.crypt
import google.auth.transport.requests
import google_auth_oauthlib
import google_auth_oauthlib.flow
import googleapiclient.http
import googleapiclient.discovery

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.helpers.osWrapper import environ

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleAuthConfig(object):
    """Google Auth config"""

    def __init__(
            self,
            serviceName: str = 'oauth2',
            scopes: list = [],
            version: str = 'v2',
            GOOGLE_CREDENTIALS_FILE: str = None,
            GOOGLE_CREDENTIALS_BASE64: str = None,
    ):
        self.serviceName: str = serviceName
        self.scopes: list[str] = scopes
        self.version: str = version

        self.GOOGLE_CREDENTIALS_FILE: str = (GOOGLE_CREDENTIALS_FILE or
                                             environ('GOOGLE_CREDENTIALS_FILE'))
        self.GOOGLE_CREDENTIALS_BASE64: str = (GOOGLE_CREDENTIALS_BASE64 or
                                               environ('GOOGLE_CREDENTIALS_BASE64'))

        self.credentials: google.oauth2.credentials.Credentials | None = None

    def __repr__(self):
        return f'{self.__dict__}'

    def __bool__(self):
        return bool(self.credentials)

    def add_scopes(self, scopes: list) -> list:
        logger.debug(f"[GoogleAuthConfig] :: add_scopes :: {scopes=} :: >>>>")
        self.scopes += scopes

        return self.scopes

    @property
    def access_token(self) -> str | None:
        if self.credentials:
            return self.credentials.token

    def _base64_to_dict(self, base64_str: str) -> dict:
        """convert credential json to dict"""
        return json.loads(base64.b64decode(base64_str))

    @property
    def credentials_file(self):
        if self.GOOGLE_CREDENTIALS_FILE:
            return self._file_to_dict(self.GOOGLE_CREDENTIALS_FILE)

        if self.GOOGLE_CREDENTIALS_BASE64:
            return self._base64_to_dict(self.GOOGLE_CREDENTIALS_BASE64)

    @property
    def credentials_file_client_id(self):

        if 'client_id' in self.credentials_file:
            return self.credentials_file['client_id']

        if 'installed' in self.credentials_file:
            return self.credentials_file['installed']['client_id']

        raise Exception(f'{self.credentials_file} is not installed')

    def _credentials_pickle_save(self):

        credentials_pickle_save = self.credentials_file_client_id + '.pickle'

        if self.credentials:
            with open(credentials_pickle_save, 'wb') as token:
                pickle.dump(self.credentials, token)
            return True

        logger.debug(
            f"[GoogleAuthConfig] :: "
            f"credentials_pickle_save :: "
            f"{credentials_pickle_save=} ({os.stat(credentials_pickle_save).st_size / 1024:.2f} KB)")

        return False

    def _credentials_pickle_load(self):

        credentials_pickle_load = self.credentials_file_client_id + '.pickle'

        if os.path.exists(credentials_pickle_load):
            with open(credentials_pickle_load, 'rb') as token:
                self.credentials = pickle.load(token)
                logger.debug(
                    f"[GoogleAuthConfig] :: "
                    f"credentials_pickle_load :: "
                    f"{credentials_pickle_load=} ({os.stat(credentials_pickle_load).st_size / 1024:.2f} KB)")
                return True

        return False

    def Credentials(self, reauth: bool = False) -> google.oauth2.credentials.Credentials:
        """return Google Credentials object"""

        self._credentials_pickle_load()

        try:
            self.refresh_token()
        except:
            pass

        if self.credentials and not self.credentials.expired and not reauth:
            return self.credentials

        scopes = self.scopes
        credentials = None
        errors = []
        while True:

            if self.GOOGLE_CREDENTIALS_FILE:
                filename = self.GOOGLE_CREDENTIALS_FILE

                try:
                    credentials = self.CredentialsFile(
                        filename=filename,
                        scopes=scopes)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

                try:
                    credentials = self.CredentialsServiceAccountFile(
                        filename=filename)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

                try:
                    credentials = self.CredentialsInstalledAppFlow(
                        filename=filename,
                        scopes=scopes)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

            elif self.GOOGLE_CREDENTIALS_BASE64:
                info = self._base64_to_dict(self.GOOGLE_CREDENTIALS_BASE64)

                try:
                    credentials = self.CredentialsInfo(
                        info=info,
                        scopes=scopes)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

                try:
                    credentials = self.CredentialsServiceAccountInfo(
                        info=info)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

                try:
                    credentials = self.CredentialsInstalledAppFlowConfig(
                        client_config=info,
                        scopes=scopes)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

            break

        if not credentials:
            raise Exception(f"[GoogleAuthConfig] :: Credentials :: ERROR :: {errors=}")

        self.credentials = credentials
        self._credentials_pickle_save()
        logger.debug(f"[GoogleAuthConfig] :: Credentials :: {credentials=}")
        return credentials

    def CredentialsFile(self, filename: str, scopes: list) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""

        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(
            filename=filename,
            scopes=scopes
        )

        logger.debug(f"[GoogleAuthConfig] :: CredentialsFile :: {credentials=}")
        return credentials

    def CredentialsInfo(self, info: dict, scopes: list) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from dict"""

        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
            info=info,
            scopes=scopes,
        )

        logger.debug(f"[GoogleAuthConfig] :: CredentialsInfo :: {credentials=}")
        return credentials

    def CredentialsInstalledAppFlow(
            self, filename: str,
            scopes: list) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""

        try:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=filename,
                scopes=scopes)
            credentials = flow.run_local_server(port=0)
        except Exception as error:
            raise Exception(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlow :: ERROR :: {error=}")

        logger.debug(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlow :: {flow=} :: {credentials=}")
        return credentials

    def CredentialsInstalledAppFlowConfig(
            self,
            client_config: dict,
            scopes: list) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""

        try:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
                client_config=client_config,
                scopes=scopes)
            credentials = flow.run_local_server(port=0)
        except Exception as error:
            raise Exception(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlowConfig :: ERROR :: {error=}")

        logger.debug(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlowConfig :: {flow=} :: {credentials=}")
        return credentials

    def CredentialsServiceAccountFile(self, filename: str) -> google.oauth2.service_account.Credentials:
        """return Credentials object for service account from file"""

        credentials = google.oauth2.service_account.Credentials.from_service_account_file(
            filename=filename
        )

        logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountFile :: {credentials=}")
        return credentials

    def CredentialsServiceAccountInfo(self, info: dict) -> google.oauth2.service_account.Credentials:
        """return Credentials object for service account from dict"""

        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            info=info
        )

        logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountInfo :: {credentials=}")
        return credentials

    def _dict_to_base64(self, input_dict: dict):
        """convert dict to base64"""
        dict_json = json.dumps(input_dict).encode()
        dict_base64 = base64.b64encode(dict_json).decode()
        return dict_base64

    def _file_to_base64(self, path: str = None):
        """convert file to base64"""

        if not path and self.GOOGLE_CREDENTIALS_FILE:
            path = self.GOOGLE_CREDENTIALS_FILE

        with open(path, 'rb') as f:
            credentials = f.read()
            credentials_base64 = base64.b64encode(credentials).decode()
            # logger.debug(f"[GoogleAuthConfig] :: file_to_base64 :: {credentials_base64=}")
            return credentials_base64

    def _file_to_dict(self, path: str = None) -> dict:
        """convert file to base64"""

        if not path and self.GOOGLE_CREDENTIALS_FILE:
            path = self.GOOGLE_CREDENTIALS_FILE

        with open(path, 'rb') as f:
            credentials = f.read()
            credentials_dict = json.loads(credentials)
            # logger.debug(f"[GoogleAuthConfig] :: file_to_base64 :: {credentials_dict=}")
            return credentials_dict

    @property
    def headers(self) -> dict:
        """authentication headers"""
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    def is_ready(self) -> bool:
        """return True if credentials are ready to use"""
        return bool(os.path.exists(self.GOOGLE_CREDENTIALS_FILE) or self.GOOGLE_CREDENTIALS_BASE64)

    def refresh_token(self) -> bool:
        """refresh token
        keep this in config
        """

        creds = self.credentials
        Request = google.auth.transport.requests.Request()

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request)
            return True

        return False
