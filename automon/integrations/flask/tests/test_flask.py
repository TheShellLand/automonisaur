import unittest

from flask import Flask

from automon.integrations.flask.boilerplate import FlaskBoilerplate
from automon.integrations.flask.config import FlaskConfig


class FlaskTest(unittest.TestCase):
    app = Flask(__name__)

    def test_FlaskBoilerplate(self):
        self.assertTrue(FlaskBoilerplate)
        self.assertTrue(FlaskBoilerplate())

    def test_ConfigFlask(self):
        self.assertTrue(FlaskConfig.javascript_compatibility(self.app))
        self.assertTrue(FlaskConfig.hash_key('blob'))
        self.assertTrue(FlaskConfig.new_secret_key())

# if __name__ == '__main__':
#     unittest.main()
