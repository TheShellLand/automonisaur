import os
import json
import base64

import google.auth.crypt
import google_auth_oauthlib
import google.oauth2.credentials
import google.oauth2.service_account

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.helpers.osWrapper import environ

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleAuthConfig(object):
    """Google Auth config"""

    def __init__(
            self,
            serviceName: str = None,
            scopes: list = None,
            version: str = None,
            GOOGLE_CREDENTIALS_FILE: str = None,
            GOOGLE_CREDENTIALS_BASE64: str = None
    ):
        self.serviceName = serviceName or 'servicemanagement'
        self.scopes = scopes or ['https://www.googleapis.com/auth/cloud-platform.read-only']
        self.version = version or 'v1'

        self.GOOGLE_CREDENTIALS_FILE = GOOGLE_CREDENTIALS_FILE or environ('GOOGLE_CREDENTIALS_FILE')
        self.GOOGLE_CREDENTIALS_BASE64 = GOOGLE_CREDENTIALS_BASE64 or environ('GOOGLE_CREDENTIALS_BASE64')

    def __repr__(self):
        return f'{self.__dict__}'

    def Credentials(self, **kwargs):
        """return Google Credentials object"""

        logger.debug(f"[GoogleAuthConfig] :: Credentials :: >>>>")

        credentials = None
        while True:

            try:
                credentials = self.CredentialsFile(self.GOOGLE_CREDENTIALS_FILE)
                if credentials:
                    break
            except:
                pass

            try:
                credentials = self.CredentialsInfo()
                if credentials:
                    break
            except:
                pass

            try:
                credentials = self.CredentialsServiceAccountFile()
                if credentials:
                    break
            except:
                pass

            try:
                credentials = self.CredentialsServiceAccountInfo()
                if credentials:
                    break
            except:
                pass

            try:
                credentials = self.CredentialsInstalledAppFlow(filename=self.GOOGLE_CREDENTIALS_FILE, **kwargs)
                if credentials:
                    break
            except:
                pass

            try:
                credentials = self.CredentialsInstalledAppFlowConfig(
                    client_config=self.base64_to_dict(self.GOOGLE_CREDENTIALS_BASE64), **kwargs)
                if credentials:
                    break
            except:
                pass

            break

        if credentials:
            logger.debug(f"[GoogleAuthConfig] :: Credentials :: {credentials=}")
            return credentials

        raise Exception(f"[GoogleAuthConfig] :: Credentials :: ERROR :: {credentials=}")

    def CredentialsFile(self, filename: str) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsFile :: >>>>")

        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(filename=filename)
        logger.debug(f"[GoogleAuthConfig] :: CredentialsFile :: {credentials=}")
        return credentials

    def CredentialsInfo(self) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from dict"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsInfo :: >>>>")

        if self.GOOGLE_CREDENTIALS_BASE64:
            credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
                self.base64_to_dict()
            )
            logger.debug(f"[GoogleAuthConfig] :: CredentialsInfo :: {credentials=}")
            return credentials

    def CredentialsInstalledAppFlow(
            self, filename: str,
            scopes: list = None) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlow :: {filename=} :: {scopes=} >>>>")

        if not scopes:
            scopes = self.scopes

        try:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=filename,
                scopes=scopes)
            credentials = flow.run_local_server(port=0)
        except Exception as error:
            raise Exception(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlow :: ERROR :: {error=}")

        logger.debug(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlow :: {flow=} :: {credentials=}")
        logger.info(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlow :: done")
        return credentials

    def CredentialsInstalledAppFlowConfig(
            self, client_config: str,
            scopes: list = None) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlowConfig :: {client_config=} :: {scopes=} >>>>")

        if not scopes:
            scopes = self.scopes

        try:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
                client_config=client_config,
                scopes=scopes)
            credentials = flow.run_local_server(port=0)
        except Exception as error:
            raise Exception(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlowConfig :: ERROR :: {error=}")

        logger.debug(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlowConfig :: {flow=} :: {credentials=}")
        logger.info(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlowConfig :: done")
        return credentials

    def CredentialsServiceAccountFile(self) -> google.oauth2.service_account.Credentials:
        """return Credentials object for service account from file"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountFile :: >>>>")

        if self.GOOGLE_CREDENTIALS_FILE:
            if os.path.exists(self.GOOGLE_CREDENTIALS_FILE):
                credentials = google.oauth2.service_account.Credentials.from_service_account_file(
                    self.GOOGLE_CREDENTIALS_FILE
                )
                logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountFile :: {credentials=}")
                return credentials

    def CredentialsServiceAccountInfo(self) -> google.oauth2.service_account.Credentials:
        """return Credentials object for service account from dict"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountInfo :: >>>>")

        if self.GOOGLE_CREDENTIALS_BASE64:
            credentials = google.oauth2.service_account.Credentials.from_service_account_info(
                self.base64_to_dict()
            )
            logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountInfo :: {credentials=}")
            return credentials

    def base64_to_dict(self, base64_str: str = None) -> dict:
        """convert credential json to dict"""
        logger.debug(f"[GoogleAuthConfig] :: base64_to_dict :: >>>>")

        if not base64_str and not self.GOOGLE_CREDENTIALS_BASE64:
            raise Exception(f'Missing GOOGLE_CREDENTIALS_BASE64')

        base64_str = base64_str or self.GOOGLE_CREDENTIALS_BASE64
        return json.loads(
            base64.b64decode(base64_str)
        )

    def dict_to_base64(self, input_dict: dict):
        """convert dict to base64"""
        logger.debug(f"[GoogleAuthConfig] :: dict_to_base64 :: >>>>")

        dict_json = json.dumps(input_dict).encode()
        dict_base64 = base64.b64encode(dict_json).decode()
        # logger.debug(f"[GoogleAuthConfig] :: dict_to_base64 :: {dict_base64=}")
        return dict_base64

    def file_to_base64(self, path: str = None):
        """convert file to base64"""
        logger.debug(f"[GoogleAuthConfig] :: file_to_base64 :: >>>>")

        if not path and self.GOOGLE_CREDENTIALS_FILE:
            path = self.GOOGLE_CREDENTIALS_FILE

        with open(path, 'rb') as f:
            credentials = f.read()
            credentials_base64 = base64.b64encode(credentials).decode()
            # logger.debug(f"[GoogleAuthConfig] :: file_to_base64 :: {credentials_base64=}")
            return credentials_base64

    def file_to_dict(self, path: str = None):
        """convert file to base64"""
        logger.debug(f"[GoogleAuthConfig] :: file_to_dict :: >>>>")

        if not path and self.GOOGLE_CREDENTIALS_FILE:
            path = self.GOOGLE_CREDENTIALS_FILE

        with open(path, 'rb') as f:
            credentials = f.read()
            credentials_dict = json.loads(credentials)
            # logger.debug(f"[GoogleAuthConfig] :: file_to_base64 :: {credentials_dict=}")
            return credentials_dict

    def is_ready(self):
        """return True if configured"""
        try:
            if self.Credentials():
                return True
        except Exception as error:
            logger.error(f'is_ready :: ERROR :: {error=}')

        return False
