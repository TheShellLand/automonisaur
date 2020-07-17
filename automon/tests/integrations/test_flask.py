import unittest

from automon.integrations.flask import new_secret_key
from automon.integrations.flask.config import javascript_compatibility
from automon.integrations.flask.hashing import hash_key


class FlaskTest(unittest.TestCase):
    def test_new_secret_key(self):
        self.assertTrue(new_secret_key())

    # def test_javascript_compatibility(self):
    #     app = newflaskapp()
    #     self.assertTrue(javascript_compatibility(app))

    def test_hash_key(self):
        self.assertTrue(hash_key('blob'))

# if __name__ == '__main__':
#     unittest.main()
