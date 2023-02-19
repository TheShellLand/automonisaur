import unittest
import hashlib

from automon.integrations.minioWrapper import MinioClient
from automon.integrations.minioWrapper.bucket import Bucket

MINIO_ENDPOINT = 'play.minio.io:9000'
MINIO_ACCESS_KEY = 'Q3AM3UQ867SPQQA43P2F'
MINIO_SECRET_KEY = 'zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG'

client = MinioClient(endpoint=MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY)
bucket = hashlib.md5(f'{MINIO_ENDPOINT}'.encode()).hexdigest()


class ClientTest(unittest.TestCase):

    def test_list_buckets(self):
        if client.is_connected():
            self.assertTrue(client.list_buckets())
            self.assertEqual(type(client.list_buckets()), list)

    def test_get_bucket(self):
        if client.is_connected():
            test = client.make_bucket(bucket)

            self.assertTrue(client.get_bucket(test))
            self.assertTrue(type(client.get_bucket(test)), Bucket)


if __name__ == '__main__':
    unittest.main()
