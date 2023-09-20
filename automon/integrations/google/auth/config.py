import os
import json
import base64

import google.auth.crypt
import google.oauth2.credentials
import google.oauth2.service_account

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from automon.log import Logging
from automon.helpers import environ

log = Logging(name='GoogleAuthConfig', level=Logging.DEBUG)


class GoogleAuthConfig(object):
    """Google Auth config"""

    def __init__(
            self,
            serviceName: str = None,
            scopes: list = None,
            version: str = None,
    ):
        self.serviceName = serviceName or 'servicemanagement'
        self.scopes = scopes or ['https://www.googleapis.com/auth/cloud-platform.read-only']
        self.version = version or 'v1'

    def __repr__(self):
        return f'{self.__dict__}'

    @property
    def Credentials(self):
        """return Google Credentials object"""
        try:
            if self.CredentialsFile():
                return self.CredentialsFile()
        except:
            pass

        try:
            if self.CredentialsInfo():
                return self.CredentialsInfo()
        except:
            pass

        try:
            if self.CredentialsServiceAccountFile():
                return self.CredentialsServiceAccountFile()
        except:
            pass

        try:
            if self.CredentialsServiceAccountInfo():
                return self.CredentialsServiceAccountInfo()
        except:
            pass

        log.error(f'Missing GOOGLE_CREDENTIALS or GOOGLE_CREDENTIALS_BASE64', enable_traceback=False)

    @property
    def _GOOGLE_CREDENTIALS(self):
        """env var GOOGLE_CREDENTIALS"""
        return environ('GOOGLE_CREDENTIALS')

    @property
    def _GOOGLE_CREDENTIALS_BASE64(self):
        """env var GOOGLE_CREDENTIALS_BASE64"""
        return environ('GOOGLE_CREDENTIALS_BASE64')

    def CredentialsFile(self) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""
        if self._GOOGLE_CREDENTIALS:
            if os.path.exists(self._GOOGLE_CREDENTIALS):
                return google.oauth2.credentials.Credentials.from_authorized_user_file(
                    self._GOOGLE_CREDENTIALS
                )

    def CredentialsInfo(self) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from dict"""
        if self._GOOGLE_CREDENTIALS_BASE64:
            return google.oauth2.credentials.Credentials.from_authorized_user_info(
                self.base64_to_dict()
            )

    def CredentialsServiceAccountFile(self) -> google.oauth2.service_account.Credentials:
        """return Credentials object for service account from file"""
        if self._GOOGLE_CREDENTIALS:
            if os.path.exists(self._GOOGLE_CREDENTIALS):
                return google.oauth2.service_account.Credentials.from_service_account_file(
                    self._GOOGLE_CREDENTIALS
                )

    def CredentialsServiceAccountInfo(self) -> google.oauth2.service_account.Credentials:
        """return Credentials object for service account from dict"""
        if self._GOOGLE_CREDENTIALS_BASE64:
            return google.oauth2.service_account.Credentials.from_service_account_info(
                self.base64_to_dict()
            )

    def base64_to_dict(self, base64_str: str = None) -> dict:
        """convert credential json to dict"""
        if not base64_str and not self._GOOGLE_CREDENTIALS_BASE64:
            raise Exception(f'Missing GOOGLE_CREDENTIALS_BASE6')

        base64_str = base64_str or self._GOOGLE_CREDENTIALS_BASE64
        return json.loads(
            base64.b64decode(base64_str)
        )

    def file_to_base64(self, path: str = None):
        """convert file to base64"""
        if not path and self._GOOGLE_CREDENTIALS:
            path = self._GOOGLE_CREDENTIALS

        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()

    def is_ready(self):
        """return True if configured"""
        if self.Credentials:
            return True
