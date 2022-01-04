import os
import urllib3

from automon.log import Logging


class MinioConfig(object):

    def __init__(self, endpoint: str = None,
                 access_key: str = None,
                 secret_key: str = None,
                 session_token: str = None,
                 secure: bool = None,
                 region: str = None,
                 http_client: urllib3.PoolManager = None):
        """Minio config
        """
        self._log = Logging(name=MinioConfig.__name__, level=Logging.ERROR)

        self.endpoint = endpoint or os.getenv('MINIO_ENDPOINT') or 'localhost'
        self.access_key = access_key or os.getenv('MINIO_ACCESS_KEY')
        self.secret_key = secret_key or os.getenv('MINIO_SECRET_KEY')
        self.session_token = session_token or os.getenv('MINIO_SESSION_TOKEN')
        self.secure = secure or os.getenv('MINIO_SECURE') or True
        self.region = region or os.getenv('MINIO_REGION')
        self.http_client = http_client or os.getenv('MINIO_HTTP_CLIENT')

        if not self.endpoint:
            self._log.warn(f'missing MINIO_ENDPOINT')

        if not self.access_key:
            self._log.warn(f'missing MINIO_ACCESS_KEY')

        if not self.secret_key:
            self._log.warn(f'missing MINIO_SECRET_KEY')

    def isConfigured(self):
        if self.endpoint and self.access_key and self.secret_key:
            return True
        return False

    def __repr__(self):
        return f'{self.endpoint} {self.region}'
