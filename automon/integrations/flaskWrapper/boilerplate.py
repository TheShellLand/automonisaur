import flask
from flask import Flask

from automon.log import Logging
from automon.integrations.flaskWrapper.config import FlaskConfig


class FlaskBoilerplate:

    def __init__(self, flask_name=__name__):
        self._log = Logging(FlaskBoilerplate.__name__, Logging.DEBUG)

        self.app = Flask(flask_name)
        self.app = FlaskConfig.javascript_compatibility(self.app)

    @property
    def request(self):
        return flask.request

    def run(self, port: int = None, debug: bool = False, **kwargs):
        return self.app.run(port=port, debug=debug, **kwargs)
