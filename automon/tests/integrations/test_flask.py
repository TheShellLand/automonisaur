import unittest

from flask import Flask

from automon.integrations.flask.boilerplate import FlaskBoilerplate
from automon.integrations.flask.config import ConfigFlask


class FlaskTest(unittest.TestCase):
    app = Flask(__name__)

    def test_FlaskBoilerplate(self):
        self.assertTrue(FlaskBoilerplate)
        self.assertTrue(FlaskBoilerplate())

    def test_ConfigFlask(self):
        self.assertTrue(ConfigFlask.javascript_compatibility(self.app))
        self.assertTrue(ConfigFlask.hash_key('blob'))
        self.assertTrue(ConfigFlask.new_secret_key())

# if __name__ == '__main__':
#     unittest.main()
