import unittest
import hashlib

from automon.integrations.minio.client import MinioClient

c = MinioClient()


class ClientTest(unittest.TestCase):

    def test_isConnected(self):
        if c.isConnected():
            self.assertTrue(c.isConnected())
        else:
            self.assertFalse(c.isConnected())

    def test_clear_bucket(self):
        if c.isConnected():
            bucket = c.make_bucket('AAAA')
            self.assertTrue(c.clear_bucket(bucket))


if __name__ == '__main__':
    unittest.main()
