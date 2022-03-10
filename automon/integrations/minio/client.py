import io
import socket
import functools

from minio import Minio
from typing import Optional

from automon.log import Logging

from .bucket import Bucket
from .object import Object, DeleteObject
from .config import MinioConfig
from .assertions import MinioAssertions

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

    def _is_connected(func):
        """Decorator that checks if MinioClient is connected
        """

        @functools.wraps(func)
        def _wrapper(self, *args, **kwargs):
            if not self.config.isReady():
                return False
            try:
                self.client.list_buckets()
                # if not self._sessionExpired() or self.client.list_buckets():
                return func(self, *args, **kwargs)
            except Exception as e:
                log.error(f'Minio client not connected. {e}')
            return False

        return _wrapper

    @_is_connected
    def download_object(self, bucket_name, file):
        """Minio object downloader
        """
        bucket_name = MinioAssertions.bucket_name(bucket_name)

        log.debug(f'[downloader] Downloading: {bucket_name}/{file.object_name}')
        return self.client.get_object(bucket_name, file.object_name)

    @_is_connected
    def get_bucket(self, bucket_name: str) -> Optional[Bucket]:
        """List Minio buckets"""
        bucket_name = MinioAssertions.bucket_name(bucket_name)
        buckets = self.list_buckets()

        for b in buckets:
            if b == bucket_name:
                log.info(f'Bucket: "{b}"')
                return b

        log.error(msg=f'Bucket "{bucket_name}" does not exist', raise_exception=False)
        return

    @_is_connected
    def isConnected(self):
        """Check if MinioClient is connected
        """
        log.info(f'Minio client OK')
        return True

    @_is_connected
    def list_buckets(self) -> [Bucket]:
        """List Minio buckets"""
        buckets = self.client.list_buckets()
        buckets = [Bucket(x) for x in buckets]

        log.info(f'Buckets total: {len(buckets)}')
        return buckets

    @_is_connected
    def list_objects(
            self,
            bucket_name: str,
            folder: str = None,
            recursive: bool = True, **kwargs) -> [Object]:
        """List Minio objects"""
        bucket_name = MinioAssertions.bucket_name(bucket_name)

        try:
            objects = self.client.list_objects(bucket_name, folder, recursive=recursive, **kwargs)
            objects = [Object(x) for x in objects]

            msg = f'Objects total: {len(objects)} (bucket: "{bucket_name}")'

            if folder:
                msg += f' Folder: "{folder}"'

            log.info(msg)
            return objects

        except Exception as e:
            log.error(f'failed to list objects. {e}')

        return

    @_is_connected
    def list_objects_generator(
            self,
            bucket_name: str,
            folder: str = None,
            recursive: bool = True,
            **kwargs) -> [Object]:
        """Generator for Minio objects"""
        bucket_name = MinioAssertions.bucket_name(bucket_name)

        try:
            objects = self.client.list_objects(bucket_name, folder, recursive=recursive, **kwargs)
            return objects

        except Exception as e:
            log.error(f'failed to list objects. {e}')

        return False

    @_is_connected
    def remove_bucket(self, bucket_name: str) -> Optional[bool]:
        bucket_name = MinioAssertions.bucket_name(bucket_name)

        try:
            self.client.remove_bucket(bucket_name)
            log.info(f'Removed bucket "{bucket_name}"')
            return True

        except Exception as e:
            log.error(f'Remove bucket "{bucket_name}" failed. {e}', enable_traceback=False)

        return

    @_is_connected
    def remove_objects(self, bucket_name, folder=None) -> bool:
        bucket_name = MinioAssertions.bucket_name(bucket_name)
        objects = self.list_objects(bucket_name, folder)
        delete_objects = [DeleteObject(x) for x in objects]

        if not delete_objects:
            log.info(f'Bucket is empty: "{bucket_name}"')
            return

        errors = list(self.client.remove_objects(bucket_name, delete_objects))
        log.info(f'Removed {len(delete_objects)} objects in bucket "{bucket_name}"')

        if self.list_objects(bucket_name, folder):
            return self.remove_objects(bucket_name, folder=folder)

        return True

    @_is_connected
    def make_bucket(self, bucket_name: str) -> Bucket:
        """Make a bucket"""
        bucket_name = MinioAssertions.bucket_name(bucket_name)
        try:
            self.client.make_bucket(bucket_name)
            log.info(f'Created bucket "{bucket_name}"')

        except Exception as e:
            log.warn(f'Bucket exists: "{bucket_name}"')

        return self.get_bucket(bucket_name)

    @_is_connected
    def put_object(self, bucket_name: str, object_name: str, data: io.BytesIO, length: int = None,
                   content_type='application/octet-stream',
                   metadata=None, sse=None, progress=None,
                   part_size=None):
        """Minio object uploader
        """

        bucket_name = MinioAssertions.bucket_name(bucket_name)
        length = length or data.getvalue().__len__()

        log.debug(f'[{self.put_object.__name__}] Uploading: {object_name}')

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

        except Exception as e:
            log.error(
                f'[{self.put_object.__name__}] Unable to save '
                f'{self.config.endpoint}/{bucket_name}/{bucket_name} '
                f'{e}',
                raise_exception=False
            )

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
