import unittest
import datetime
import hashlib

from automon.integrations.minio import MinioClient
from automon.integrations.minio.bucket import Bucket

MINIO_ENDPOINT = 'play.minio.io:9000'
MINIO_ACCESS_KEY = 'Q3AM3UQ867SPQQA43P2F'
MINIO_SECRET_KEY = 'zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG'

c = MinioClient(endpoint=MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY)
bucket = hashlib.md5(f'{datetime.datetime.now()}'.encode()).hexdigest()


class ClientTest(unittest.TestCase):

    def test_remove_bucket(self):
        if c.isConnected():
            test = c.make_bucket(bucket)
            c.remove_objects(test)
            self.assertTrue(c.remove_bucket(test))


if __name__ == '__main__':
    unittest.main()
