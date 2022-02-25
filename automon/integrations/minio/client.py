import io
import socket
import datetime
import functools

from minio import Minio

from automon.log import Logging

from .config import MinioConfig
from .bucket import Bucket

log = Logging(name='MinioClient', level=Logging.DEBUG)


class MinioClient(object):

    def __init__(self,
                 endpoint: str = None,
                 access_key: str = None,
                 secret_key: str = None,
                 config: MinioConfig = None):
        """Minio client"""

        self.config = config or MinioConfig(endpoint=endpoint, access_key=access_key, secret_key=secret_key)

    def __repr__(self):
        return f'endpoint: {self.config.endpoint}'

    @property
    def client(self):
        client = Minio(
            endpoint=self.config.endpoint,
            access_key=self.config.access_key,
            secret_key=self.config.secret_key,
            session_token=self.config.session_token,
            secure=self.config.secure,
            region=self.config.region,
            http_client=self.config.http_client
        )
        return client

    def _isConnected(func):
        """Decorator that checks if MinioClient is connected
        """

        @functools.wraps(func)
        def _wrapper(self, *args, **kwargs):
            if self.config.isReady():
                if self.client.list_buckets():
                    # if not self._sessionExpired() or self.client.list_buckets():
                    return func(self, *args, **kwargs)

        return _wrapper

    @_isConnected
    def clear_bucket(self, bucket_name, folder=None):
        objects = self.list_objects(bucket_name, folder)
        for a in objects:
            print(a)
        return self.client.remove_objects(bucket_name, objects)

    @_isConnected
    def download_object(self, bucket, file):
        """ Minio object downloader
        """
        log.debug(f'[downloader] Downloading: {bucket}/{file.object_name}')
        return self.client.get_object(bucket, file.object_name)

    @_isConnected
    def isConnected(self):
        """Check if MinioClient is connected
        """
        log.info(f'Minio client OK')
        return True

    @_isConnected
    def list_objects(self, bucket: str, folder: str = None, recursive: bool = True):
        """ List Minio objects
        """
        log.debug(f'[list_all_objects] bucket: {bucket}, folder: {folder}')
        return self.client.list_objects(bucket, folder, recursive=recursive)

    @_isConnected
    def list_buckets(self) -> [Bucket]:
        """ List Minio buckets
        """
        buckets = self.client.list_buckets()
        buckets = [Bucket(x) for x in buckets]

        log.info(f'buckets: {len(buckets)} {[x.name for x in buckets]}')
        return buckets

    @_isConnected
    def get_bucket(self, bucket: str) -> Bucket:
        """ List Minio buckets
        """
        buckets = self.list_buckets()

        for b in buckets:
            if b == bucket:
                log.info(f'buckets: {len(buckets)} {[x.name for x in buckets]}')
                return b

        log.error(msg=f'bucket does not exist {bucket}', raise_exception=False)
        return False

    @_isConnected
    def make_bucket(self, bucket_name) -> bool:
        try:
            log.debug(f'Created bucket: {bucket_name}')
            self.client.make_bucket(bucket_name)
            return True

        except Exception as e:
            log.error(f'Bucket exists: {bucket_name} {e}', enable_traceback=False)
            return False

    @_isConnected
    def put_object(self, bucket_name: str, object_name: str, data: io.BytesIO, length: int = None,
                   content_type='application/octet-stream',
                   metadata=None, sse=None, progress=None,
                   part_size=None):
        """ Minio object uploader
        """

        log.debug(f'[{self.put_object.__name__}] Uploading: {object_name}')

        length = length or data.getvalue().__len__()

        try:
            put = self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data, length=length,
                content_type=content_type,
                metadata=metadata, sse=sse,
                progress=progress)
            log.info(
                f'[put_object] Saved to '
                f'{self.config.endpoint}/{bucket_name}/{object_name}'
            )

            return put

        except Exception as _:
            log.error(
                f'[{self.put_object.__name__}] Unable to save '
                f'{self.config.endpoint}/{bucket_name}/{bucket_name}'
            )

            return False

    @_isConnected
    def remove_bucket(self, bucket_name) -> bool:
        try:
            log.info(f'Removed bucket: {bucket_name}')
            self.client.remove_bucket(bucket_name)
            return True

        except Exception as e:
            log.error(f'Bucket does not exist: {bucket_name} {e}', enable_traceback=False)
            return False


def check_connection(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
        return True
    except Exception as e:
        log.error(e, enable_traceback=False)
        return False
