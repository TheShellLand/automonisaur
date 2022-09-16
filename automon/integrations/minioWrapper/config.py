import os
import urllib3

from automon.log import Logging
from automon.helpers import environ

log = Logging(name='MinioConfig', level=Logging.ERROR)


class MinioConfig(object):

    def __init__(self, endpoint: str = None,
                 access_key: str = None,
                 secret_key: str = None,
                 session_token: str = None,
                 secure: bool = None,
                 region: str = None,
                 http_client: urllib3.PoolManager = None):
        """Minio config"""

        self.endpoint = endpoint or environ('MINIO_ENDPOINT', 'localhost')
        self.access_key = access_key or environ('MINIO_ACCESS_KEY')
        self.secret_key = secret_key or environ('MINIO_SECRET_KEY')
        self.session_token = session_token or environ('MINIO_SESSION_TOKEN')
        self.secure = secure or environ('MINIO_SECURE', True)
        self.region = region or environ('MINIO_REGION')
        self.http_client = http_client or environ('MINIO_HTTP_CLIENT')

        if not self.endpoint:
            log.warn(f'missing MINIO_ENDPOINT')

        if not self.access_key:
            log.warn(f'missing MINIO_ACCESS_KEY')

        if not self.secret_key:
            log.warn(f'missing MINIO_SECRET_KEY')

    def isReady(self):
        if self.endpoint and self.access_key and self.secret_key:
            return True
        return False

    def __repr__(self):
        return f'{self.__dict__}'
