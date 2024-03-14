from automon import log
from automon.helpers import environ

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class SwimlaneConfig(object):

    def __init__(
            self,
            host: str = None,
            userName: str = '',
            password: str = '',
            apiKey: str = None,
            jwt_token: str = None,
    ):
        self.host = host or environ('SWIMLANE_HOST')
        self.userName = userName or environ('SWIMLANE_USERNAME', '')
        self.password = password or environ('SWIMLANE_PASSWORD', '')
        self.apiKey = apiKey or environ('SWIMLANE_APIKEY')
        self.jwt_token = jwt_token or environ('SWIMLANE_JWT_TOKEN', 'missing SWIMLANE_JWT_TOKEN')

        self.userName_model = None

        self.appId = environ('SWIMLANE_APP_ID')

    @property
    def bearer_token(self):
        return self.token

    @property
    def credentials(self):
        return {
            'userName': self.userName,
            'password': self.password,
        }

    @property
    def token(self):
        return self.apiKey

    @property
    def headers(self):
        if self.token:
            return {
                'Authorization': f'Bearer {self.apiKey}'
            }

        if self.private_token:
            return {
                'Authorization': f'Bearer {self.jwt_token}',
                'Content-Type': 'application/json'
            }

    @property
    def headers_jwt_token(self):
        if self.private_token:
            return {
                'Authorization': f'Bearer {self.jwt_token}',
                'Content-Type': 'application/json'
            }

    async def is_ready(self) -> bool:
        if self.host:
            if self.userName and self.password:
                return True
            if self.apiKey:
                return True
            if self.jwt_token:
                return True

        logger.error(str(dict(
            host=self.host,
            userName=self.userName,
            password=self.password,
            apiKey=self.apiKey,
            jwt_token=self.jwt_token,
        )))
        return False

    @property
    def private_token(self):
        return self.jwt_token
