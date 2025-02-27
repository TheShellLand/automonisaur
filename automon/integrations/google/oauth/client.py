import automon
import warnings
import functools
import googleapiclient.http
import googleapiclient.discovery
import google.auth.transport.requests

from automon.helpers.loggingWrapper import LoggingClient, DEBUG

from .config import GoogleAuthConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


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
            if self.authenticate_oauth():
                return self.authenticate_oauth()
        except Exception as error:
            raise error

        try:
            if self.authenticate_service_account():
                return self.authenticate_service_account()
        except Exception as error:
            raise error

        return False

    def authenticate_oauth(self) -> bool:
        """authenticate web token"""

        creds = self.config.Credentials()
        Request = google.auth.transport.requests.Request()

        if hasattr(creds, 'refresh_token'):
            try:
                creds.refresh(Request)
                logger.info(f'[google] :: auth :: oauth :: token refresh :: {getattr(creds, "refresh_token")}')
                logger.info(f'[google] :: auth :: oauth :: token refresh :: done')
                return True
            except Exception as error:
                logger.error(msg=f'[google] :: auth :: oauth :: error :: token refresh failed: {error}')

        else:
            logger.warning(f'[google] :: auth :: TODO: add google flow() authentication')
            logger.info(f'[google] :: auth :: oauth :: done')
            return True

        return False

    def authenticate_service_account(self) -> bool:
        """authenticate service account"""
        if self.config.Credentials():
            return True
        return False

    def is_ready(self) -> bool:
        """Check if authenticated to make requests"""
        try:
            return self.authenticate()
        except Exception as error:
            logger.error(f'[google] :: is_connected :: ERROR :: {error=}')

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
            credentials=credentials or self.config.Credentials(),
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
