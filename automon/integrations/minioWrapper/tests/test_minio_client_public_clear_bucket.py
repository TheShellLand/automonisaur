import unittest
import datetime
import hashlib

from automon.integrations.minioWrapper import MinioClient
from automon.integrations.minioWrapper.bucket import Bucket

MINIO_ENDPOINT = 'play.minio.io:9000'
MINIO_ACCESS_KEY = 'Q3AM3UQ867SPQQA43P2F'
MINIO_SECRET_KEY = 'zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG'

c = MinioClient(endpoint=MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY)
bucket = hashlib.md5(f'{datetime.datetime.now()}'.encode()).hexdigest()


class ClientTest(unittest.TestCase):

    def test_remove_bucket(self):
        if c.is_connected():
            test = c.make_bucket(bucket)
            bucket_name = test.name
            c.remove_objects(bucket_name)
            self.assertTrue(c.remove_bucket(bucket_name))


if __name__ == '__main__':
    unittest.main()
