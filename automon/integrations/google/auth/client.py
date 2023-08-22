import functools
import googleapiclient.http
import googleapiclient.discovery
import google.auth.transport.requests

from automon.log import Logging

from .config import GoogleAuthConfig

log = Logging(name='GoogleAuthClient', level=Logging.DEBUG)


class GoogleAuthClient(object):
    """Google Auth client"""

    def __init__(
            self,
            config: GoogleAuthConfig = None,
            serviceName: str = None,
            scopes: list = None,
            version: str = None,
            **kwargs,
    ):

        self.config = config or GoogleAuthConfig(
            serviceName=serviceName,
            scopes=scopes,
            version=version,
            **kwargs
        )

    def __repr__(self):
        return f'{self.__dict__}'

    @classmethod
    def execute(cls, func):
        return func.execute()

    def _is_connected(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.authenticate():
                return func(self, *args, **kwargs)

        return wrapped

    def authenticate(self) -> bool:
        """authenticate with credentials"""

        try:
            return self.authenticate_oauth()
        except:
            pass

        try:
            return self.authenticate_service_account()
        except:
            pass

        return False

    def authenticate_oauth(self) -> bool:
        """authenticate web token"""

        creds = self.config.Credentials
        refresh_token = creds.refresh_token

        if refresh_token:
            try:
                creds.refresh(google.auth.transport.requests.Request())
                log.info(f'token refresh success')
                return True
            except Exception as e:
                log.error(msg=f'token refresh failed: {e}', enable_traceback=False)

        else:
            # TODO: add google flow() authentication here
            log.info(f'flow login success')
            return True

        return False

    def authenticate_service_account(self) -> bool:
        """authenticate service account"""
        if self.config.Credentials:
            return True
        return False

    def is_connected(self) -> bool:
        """Check if authenticated to make requests"""
        return self.authenticate()

    def service(
            self,
            serviceName: str = None,
            version: str = None,
            http=None,
            discoveryServiceUrl=None,
            developerKey=None,
            model=None,
            requestBuilder=None,
            credentials=None,
            cache_discovery=True,
            cache=None,
            client_options=None,
            adc_cert_path=None,
            adc_key_path=None,
            num_retries=1,
            static_discovery=None,
            always_use_jwt_access=False,
            **kwargs
    ) -> googleapiclient.discovery.build:
        return googleapiclient.discovery.build(
            serviceName=serviceName or self.config.serviceName,
            version=version or self.config.version,
            http=http,
            discoveryServiceUrl=discoveryServiceUrl,
            developerKey=developerKey,
            model=model,
            requestBuilder=requestBuilder or googleapiclient.http.HttpRequest,
            credentials=credentials or self.config.Credentials,
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
