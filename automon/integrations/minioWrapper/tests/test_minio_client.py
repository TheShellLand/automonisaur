import unittest
import hashlib

from automon.integrations.minioWrapper.client import MinioClient

c = MinioClient()


class ClientTest(unittest.TestCase):

    def test_isConnected(self):
        if c.is_connected():
            self.assertTrue(c.is_connected())
        else:
            self.assertFalse(c.is_connected())

    def test_clear_bucket(self):
        if c.is_connected():
            bucket = c.make_bucket('AAAAAA')
            if c.list_objects(bucket):
                self.assertTrue(c.remove_objects(bucket))
            else:
                self.assertFalse(c.remove_objects(bucket))


if __name__ == '__main__':
    unittest.main()
