import functools
import googleapiclient.http
import googleapiclient.discovery
import google.auth.transport.requests

from automon import log

from .config import GoogleAuthConfig

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


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
    async def execute(cls, func):
        return await func.execute()

    async def _is_connected(func):
        @functools.wraps(func)
        async def wrapped(self, *args, **kwargs):
            if self.authenticate():
                return await func(self, *args, **kwargs)

        return wrapped

    async def authenticate(self) -> bool:
        """authenticate with credentials"""

        try:
            return await self.authenticate_oauth()
        except:
            pass

        try:
            return await self.authenticate_service_account()
        except:
            pass

        return False

    async def authenticate_oauth(self) -> bool:
        """authenticate web token"""

        creds = await self.config.Credentials()
        refresh_token = creds.refresh_token

        if refresh_token:
            try:
                creds.refresh(google.auth.transport.requests.Request())
                logger.info(f'token refresh success')
                return True
            except Exception as e:
                logger.error(msg=f'token refresh failed: {e}')

        else:
            # TODO: add google flow() authentication here
            logger.info(f'flow login success')
            return True

        return False

    async def authenticate_service_account(self) -> bool:
        """authenticate service account"""
        if await self.config.Credentials():
            return True
        return False

    async def is_connected(self) -> bool:
        """Check if authenticated to make requests"""
        return await self.authenticate()

    async def service(
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
            credentials=credentials or await self.config.Credentials(),
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
