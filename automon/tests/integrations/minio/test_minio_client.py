import unittest
import hashlib

from automon.integrations.minio.client import MinioClient


class Client(unittest.TestCase):

    def test_MinioClient(self):
        self.assertTrue(MinioClient())
        self.assertTrue(MinioClient)

    def test_publicServer(self):
        MINIO_ENDPOINT = 'play.minio.io:9000'
        MINIO_ACCESS_KEY = 'Q3AM3UQ867SPQQA43P2F'
        MINIO_SECRET_KEY = 'zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG'

        m = MinioClient(endpoint=MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY)
        bucket = hashlib.md5(f'{MINIO_ENDPOINT}'.encode()).hexdigest()

        if m.isConnected():

            self.assertTrue(len(m.list_buckets()) >= 0)   # this might fail if no buckets
            self.assertTrue(type(m.list_buckets()), list)
            self.assertTrue(type(m.list_buckets(bucket)), list)

            if m.list_buckets(bucket):
                self.assertTrue(m.remove_bucket(bucket))
            else:
                self.assertTrue(m.make_bucket(bucket))


if __name__ == '__main__':
    unittest.main()
