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
            bucket = c.make_bucket('AAAAAA')
            if c.list_objects(bucket):
                self.assertTrue(c.remove_objects(bucket))
            else:
                self.assertFalse(c.remove_objects(bucket))


if __name__ == '__main__':
    unittest.main()
