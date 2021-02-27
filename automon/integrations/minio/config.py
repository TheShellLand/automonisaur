import os
import urllib3

from automon.log.logger import Logging


class MinioConfig:

    def __init__(self, endpoint: str = None, access_key: str = None, secret_key: str = None,
                 session_token: str = None, secure: bool = None, region: str = None,
                 http_client: urllib3.PoolManager = None):
        """"""
        self._log = Logging(name=MinioConfig.__name__, level=Logging.ERROR)

        self.endpoint = endpoint or os.getenv('MINIO_ENDPOINT')
        self.access_key = access_key or os.getenv('MINIO_ACCESS_KEY')
        self.secret_key = secret_key or os.getenv('MINIO_SECRET_KEY')
        self.session_token = session_token or os.getenv('MINIO_SESSION_TOKEN')
        self.secure = secure or os.getenv('MINIO_SECURE') or True
        self.region = region or os.getenv('MINIO_REGION')
        self.http_client = http_client or os.getenv('MINIO_HTTP_CLIENT')

        if not self.endpoint:
            self._log.error(f'missing MINIO_ENDPOINT')

        if not self.access_key:
            self._log.error(f'missing MINIO_ACCESS_KEY')

        if not self.secret_key:
            self._log.error(f'missing MINIO_SECRET_KEY')

    def __repr__(self):
        return f'{self.endpoint} {self.region}'


def use_public_server():
    return MinioConfig(
        endpoint='play.minio.io:9000',
        access_key='Q3AM3UQ867SPQQA43P2F',
        secret_key='zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG')
