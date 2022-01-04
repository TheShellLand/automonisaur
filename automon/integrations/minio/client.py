import io
import socket
import datetime
import functools

from minio import Minio

from automon.log import Logging
from automon.integrations.minio.config import MinioConfig

log = Logging(name='minio', level=Logging.INFO)


class MinioClient(object):

    def __init__(self, endpoint: str = None,
                 access_key: str = None,
                 secret_key: str = None,
                 config: MinioConfig = None):
        """Minio client
        """

        self._log = Logging(name=MinioClient.__name__, level=Logging.DEBUG)

        self.config = config or MinioConfig(endpoint=endpoint, access_key=access_key, secret_key=secret_key)

        self.client = self._client()
        self._lastClientCheck = None

    def __repr__(self):
        return f'endpoint: {self.config.endpoint} connected: {self.isConnected()}'

    def _client(self):
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

    def _sessionExpired(self):
        if not self._lastClientCheck:
            self._lastClientCheck = datetime.datetime.now()
            return True

        isExpired = self._lastClientCheck + datetime.timedelta(minutes=5)
        if self._lastClientCheck > isExpired:
            return True
        return False

    def isConnected(func):
        """Decorator that checks if MinioClient is connected
        """

        @functools.wraps(func)
        def _wrapper(self, *args, **kwargs):
            if not self._sessionExpired() or self.client.list_buckets():
                return func(self, *args, **kwargs)

        return _wrapper

    @isConnected
    def download_object(self, bucket, file):
        """ Minio object downloader
        """
        self._log.logging.debug(f'[downloader] Downloading: {bucket}/{file.object_name}')
        return self.client.get_object(bucket, file.object_name)

    @isConnected
    def list_objects(self, bucket: str, folder: str = None, recursive: bool = True):
        """ List Minio objects
        """
        self._log.logging.debug(f'[list_all_objects] bucket: {bucket}, folder: {folder}')
        return self.client.list_objects(bucket, folder, recursive=recursive)

    @isConnected
    def list_buckets(self, bucket: str = None) -> list:
        """ List Minio buckets
        """
        buckets = self.client.list_buckets()

        if bucket:
            self._log.debug(f'bucket name: {bucket}')
            return [x for x in buckets if x == bucket]

        self._log.logging.debug(f'buckets: {len(buckets)} {[x.name for x in buckets]}')
        return buckets

    @isConnected
    def put_object(self, bucket_name: str, object_name: str, data: io.BytesIO, length: int = None,
                   content_type='application/octet-stream',
                   metadata=None, sse=None, progress=None,
                   part_size=None):
        """ Minio object uploader
        """

        self._log.debug(f'[{self.put_object.__name__}] Uploading: {object_name}')

        length = length or data.getvalue().__len__()

        try:
            put = self.client.put_object(bucket_name=bucket_name, object_name=object_name,
                                         data=data, length=length,
                                         content_type=content_type,
                                         metadata=metadata, sse=sse, progress=progress)
            self._log.info(
                f'[put_object] Saved to '
                f'{self.client._endpoint_url}/{bucket_name}/{object_name}'
            )

            return put

        except Exception as _:
            self._log.error(
                f'[{self.put_object.__name__}] Unable to save '
                f'{self.client._endpoint_url}/{bucket_name}/{bucket_name}'
            )

            return False

    @isConnected
    def clear_bucket(self, bucket_name, folder=None):
        objects = self.list_objects(bucket_name, folder)
        for a in objects:
            print(a)
        return self.client.remove_objects(bucket_name, objects)

    @isConnected
    def make_bucket(self, bucket_name) -> bool:
        try:
            self._log.debug(f'Created bucket: {bucket_name}')
            self.client.make_bucket(bucket_name)
            return True

        except Exception as e:
            self._log.error(f'Bucket exists: {bucket_name} {e}', enable_traceback=False)
            return False

    @isConnected
    def remove_bucket(self, bucket_name) -> bool:
        try:
            self._log.debug(f'Removed bucket: {bucket_name}')
            self.client.remove_bucket(bucket_name)
            return True

        except Exception as e:
            self._log.error(f'Bucket does not exist: {bucket_name} {e}', enable_traceback=False)
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
