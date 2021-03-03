import io
import socket

from minio import Minio
from urllib.parse import urlparse

from automon.log.logger import Logging
from automon.integrations.minio.config import MinioConfig

log = Logging(name='minio', level=Logging.INFO)


class MinioClient:

    def __init__(self, config: MinioConfig = None):
        self._log = Logging(name=MinioClient.__name__, level=Logging.DEBUG)

        self.config = config or MinioConfig()

        check = urlparse(self.config.endpoint)
        if check_connection(check.hostname, check.port):
            self.client = Minio(
                endpoint=self.config.endpoint,
                access_key=self.config.access_key,
                secret_key=self.config.secret_key,
                session_token=self.config.session_token,
                secure=self.config.secure,
                region=self.config.region,
                http_client=self.config.http_client
            )
            self.connected = True
        else:
            self.connected = False

    def download_object(self, bucket, file):
        """ Minio object downloader
        """
        self._log.logging.debug(
            f'[downloader] Downloading: {bucket}/{file.object_name}')
        return self.client.get_object(bucket, file.object_name)

    def list_all_objects(self, bucket: str, folder: str = None, recursive: bool = True):
        """ List Minio objects
        """
        self._log.logging.debug(f'[list_all_objects] bucket: {bucket}, folder: {folder}')
        return self.client.list_objects(bucket, folder, recursive=recursive)

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

    def clear_bucket(self, bucket_name, folder=None):
        objects = self.list_all_objects(bucket_name, folder)
        for a in objects:
            print(a)
        return self.client.remove_objects(bucket_name, objects)

    def make_bucket(self, bucket_name):
        try:
            self.client.make_bucket(bucket_name)
            self._log.debug(f'[make_bucket] Created bucket: {bucket_name}')
            return True

        except Exception as _:
            self._log.debug(f'[make_bucket] Bucket exists: {bucket_name}')
            return False


def check_connection(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
        return True
    except Exception as _:
        return False
