import unittest
import hashlib

from automon.integrations.minio import MinioClient
from automon.integrations.minio.bucket import Bucket

MINIO_ENDPOINT = 'play.minio.io:9000'
MINIO_ACCESS_KEY = 'Q3AM3UQ867SPQQA43P2F'
MINIO_SECRET_KEY = 'zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG'

c = MinioClient(endpoint=MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY)
bucket = hashlib.md5(f'{MINIO_ENDPOINT}'.encode()).hexdigest()


class ClientTest(unittest.TestCase):

    def test_list_buckets(self):
        if c.isConnected():
            self.assertTrue(c.list_buckets())
            self.assertEqual(type(c.list_buckets()), list)

    def test_get_bucket(self):
        if c.isConnected():
            test = c.make_bucket(bucket)

            self.assertTrue(c.get_bucket(test))
            self.assertTrue(type(c.get_bucket(test)), Bucket)


if __name__ == '__main__':
    unittest.main()
