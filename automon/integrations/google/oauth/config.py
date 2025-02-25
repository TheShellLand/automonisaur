import json
import base64

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
            scopes: list = None,
            version: str = 'v2',
            GOOGLE_CREDENTIALS_FILE: str = None,
            GOOGLE_CREDENTIALS_BASE64: str = None
    ):
        self.serviceName = serviceName
        self.scopes = scopes
        self.version = version

        self.GOOGLE_CREDENTIALS_FILE = GOOGLE_CREDENTIALS_FILE or environ('GOOGLE_CREDENTIALS_FILE')
        self.GOOGLE_CREDENTIALS_BASE64 = GOOGLE_CREDENTIALS_BASE64 or environ('GOOGLE_CREDENTIALS_BASE64')

        self.credentials: google.oauth2.credentials.Credentials = None

        self._userinfo = None

        if scopes is None:
            self.scopes = [
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
            ]

    def add_scopes(self, scopes: list) -> list:
        logger.debug(f"[GoogleAuthConfig] :: add_scopes :: {scopes=} :: >>")
        self.scopes += scopes

        return self.scopes

    def __repr__(self):
        return f'{self.__dict__}'

    def Credentials(self) -> google.oauth2.credentials.Credentials:
        """return Google Credentials object"""

        logger.debug(f"[GoogleAuthConfig] :: Credentials :: >>")

        if self.credentials:
            return self.credentials

        scopes = self.scopes
        credentials = None
        errors = []
        while True:

            if self.GOOGLE_CREDENTIALS_FILE:
                filename = self.GOOGLE_CREDENTIALS_FILE

                try:
                    credentials = self.CredentialsFile(filename=filename,
                                                       scopes=scopes)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

                try:
                    credentials = self.CredentialsServiceAccountFile(filename=filename)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

                try:
                    credentials = self.CredentialsInstalledAppFlow(filename=filename,
                                                                   scopes=scopes)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

            elif self.GOOGLE_CREDENTIALS_BASE64:
                info = self.base64_to_dict(self.GOOGLE_CREDENTIALS_BASE64)

                try:
                    credentials = self.CredentialsInfo(info=info,
                                                       scopes=scopes)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

                try:
                    credentials = self.CredentialsServiceAccountInfo(info=info)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

                try:
                    credentials = self.CredentialsInstalledAppFlowConfig(client_config=info,
                                                                         scopes=scopes)
                    if credentials:
                        break
                except Exception as error:
                    errors.append(error)

            break

        if credentials:
            logger.debug(f"[GoogleAuthConfig] :: Credentials :: {credentials=}")
            logger.info(f"[GoogleAuthConfig] :: Credentials :: done")
            self.credentials = credentials
            return credentials

        raise Exception(f"[GoogleAuthConfig] :: Credentials :: ERROR :: {errors=}")

    def CredentialsFile(self, filename: str, scopes: list) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsFile :: {filename=} :: {len(scopes)} scopes >>")

        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(
            filename=filename,
            scopes=scopes
        )

        logger.debug(f"[GoogleAuthConfig] :: CredentialsFile :: {credentials=}")
        logger.info(f"[GoogleAuthConfig] :: CredentialsFile :: done")
        return credentials

    def CredentialsInfo(self, info: dict, scopes: list) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from dict"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsInfo :: {len(scopes)} scopes :: >>")

        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
            info=info,
            scopes=scopes,
        )

        logger.debug(f"[GoogleAuthConfig] :: CredentialsInfo :: {credentials=}")
        logger.info(f"[GoogleAuthConfig] :: CredentialsInfo :: done")
        return credentials

    def CredentialsInstalledAppFlow(
            self, filename: str,
            scopes: list) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlow :: {filename=} :: {len(scopes)} scopes >>")

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
            self,
            client_config: dict,
            scopes: list) -> google.oauth2.credentials.Credentials:
        """return Credentials object for web auth from file"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsInstalledAppFlowConfig :: {len(scopes)} scopes :: >>")

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

    def CredentialsServiceAccountFile(self, filename: str) -> google.oauth2.service_account.Credentials:
        """return Credentials object for service account from file"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountFile :: {filename=} :: >>")

        credentials = google.oauth2.service_account.Credentials.from_service_account_file(
            filename=filename
        )

        logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountFile :: {credentials=}")
        logger.info(f"[GoogleAuthConfig] :: CredentialsServiceAccountFile :: done")
        return credentials

    def CredentialsServiceAccountInfo(self, info: dict) -> google.oauth2.service_account.Credentials:
        """return Credentials object for service account from dict"""
        logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountInfo :: >>")

        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            info=info
        )

        logger.debug(f"[GoogleAuthConfig] :: CredentialsServiceAccountInfo :: {credentials=}")
        logger.info(f"[GoogleAuthConfig] :: CredentialsServiceAccountInfo :: done")
        return credentials

    def base64_to_dict(self, base64_str: str) -> dict:
        """convert credential json to dict"""
        logger.debug(f"[GoogleAuthConfig] :: base64_to_dict :: >>")

        return json.loads(
            base64.b64decode(base64_str)
        )

    def dict_to_base64(self, input_dict: dict):
        """convert dict to base64"""
        logger.debug(f"[GoogleAuthConfig] :: dict_to_base64 :: >>")

        dict_json = json.dumps(input_dict).encode()
        dict_base64 = base64.b64encode(dict_json).decode()

        logger.info(f"[GoogleAuthConfig] :: dict_to_base64 :: done")
        return dict_base64

    def file_to_base64(self, path: str = None):
        """convert file to base64"""
        logger.debug(f"[GoogleAuthConfig] :: file_to_base64 :: >>")

        if not path and self.GOOGLE_CREDENTIALS_FILE:
            path = self.GOOGLE_CREDENTIALS_FILE

        with open(path, 'rb') as f:
            credentials = f.read()
            credentials_base64 = base64.b64encode(credentials).decode()
            # logger.debug(f"[GoogleAuthConfig] :: file_to_base64 :: {credentials_base64=}")
            return credentials_base64

    def file_to_dict(self, path: str = None):
        """convert file to base64"""
        logger.debug(f"[GoogleAuthConfig] :: file_to_dict :: >>")

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
            if self.GOOGLE_CREDENTIALS_FILE or self.GOOGLE_CREDENTIALS_BASE64:
                return True
        except Exception as error:
            logger.error(f'[GoogleAuthConfig] :: is_ready :: ERROR :: {error=}')

        return False

    def build_service(
            self,
            serviceName: str = None,
            version: str = None,
            http=None,
            discoveryServiceUrl=None,
            developerKey=None,
            model=None,
            requestBuilder=None,
            credentials: dict = None,
            cache_discovery=True,
            cache=None,
            client_options=None,
            adc_cert_path=None,
            adc_key_path=None,
            num_retries=1,
            static_discovery=None,
            always_use_jwt_access=False,
            **kwargs) -> googleapiclient.discovery.build:
        logger.debug(f'[GoogleAuthConfig] :: build_service :: {serviceName=} :: {version=} :: {credentials=} :: >>')
        service = googleapiclient.discovery.build(
            serviceName=serviceName or self.serviceName,
            version=version or self.version,
            http=http,
            discoveryServiceUrl=discoveryServiceUrl,
            developerKey=developerKey,
            model=model,
            requestBuilder=requestBuilder or googleapiclient.http.HttpRequest,
            credentials=credentials or self.credentials,
            cache_discovery=cache_discovery,
            cache=cache,
            client_options=client_options,
            adc_cert_path=adc_cert_path,
            adc_key_path=adc_key_path,
            num_retries=num_retries,
            static_discovery=static_discovery,
            always_use_jwt_access=always_use_jwt_access,
            **kwargs,
        )

        logger.debug(f'[GoogleAuthConfig] :: build_service :: {service=}')
        logger.info(f'[GoogleAuthConfig] :: build_service :: done')
        return service

    def userinfo(self):
        logger.debug(f'[GoogleAuthConfig] :: userinfo :: >>')

        service = self.build_service(serviceName='oauth2', version='v2', credentials=self.credentials)
        userinfo = service.userinfo().get().execute()

        user_info = service.userinfo().get().execute()
        self._userinfo = userinfo
        return user_info

    def refresh_token(self):
        logger.debug(f'[GoogleAuthConfig] :: refresh :: >>')

        creds = self.credentials
        Request = google.auth.transport.requests.Request()

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request)
            except Exception as error:
                raise Exception(f'[GoogleAuthConfig] :: refresh :: ERROR :: {error=}')

        logger.info(f'[GoogleAuthConfig] :: refresh :: done')
        return True
