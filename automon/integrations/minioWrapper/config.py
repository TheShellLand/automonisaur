import os
import urllib3

from automon.log import Logging
from automon.helpers import environ

log = Logging(name='MinioConfig', level=Logging.ERROR)


class MinioConfig(object):
    endpoint: str
    access_key: str
    secret_key: str
    session_token: str
    secure: bool
    region: str
    http_client: urllib3.PoolManager

    def __init__(self, endpoint: str = None,
                 access_key: str = None,
                 secret_key: str = None,
                 session_token: str = None,
                 secure: bool = None,
                 region: str = None,
                 http_client: urllib3.PoolManager = None):
        """Minio config"""

        self._endpoint = endpoint or environ('MINIO_ENDPOINT', 'localhost')
        self._access_key = access_key or environ('MINIO_ACCESS_KEY')
        self._secret_key = secret_key or environ('MINIO_SECRET_KEY')
        self._session_token = session_token or environ('MINIO_SESSION_TOKEN')
        self._secure = secure or environ('MINIO_SECURE', True)
        self._region = region or environ('MINIO_REGION')
        self._http_client = http_client or environ('MINIO_HTTP_CLIENT')

        if not self.endpoint:
            log.warning(f'missing MINIO_ENDPOINT')

        if not self.access_key:
            log.warning(f'missing MINIO_ACCESS_KEY')

        if not self.secret_key:
            log.warning(f'missing MINIO_SECRET_KEY')

    @property
    def access_key(self):
        return self._access_key

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def is_ready(self):
        if self.endpoint and self.access_key and self.secret_key:
            return True
        return False

    @property
    def secret_key(self):
        return self._secret_key

    @property
    def secure(self):
        return self._secure

    @property
    def session_token(self):
        return self._session_token

    @property
    def region(self):
        return self._region

    @property
    def http_client(self):
        return self._http_client

    def __repr__(self):
        return f'{self.__dict__}'
