import flask
from flask import Flask

from automon.log import Logging
from automon.integrations.flaskWrapper.config import FlaskConfig


class FlaskBoilerplate(object):

    def __init__(self, flask_name=__name__,
                 enable_javascript_compatibility: bool = False,
                 config: FlaskConfig = None, **kwargs):
        """Wrapper for flask"""
        self._log = Logging(FlaskBoilerplate.__name__, Logging.DEBUG)

        self.Flask = Flask(flask_name, **kwargs)
        self.config = config or FlaskConfig()

        if enable_javascript_compatibility:
            self.Flask = FlaskConfig.javascript_compatibility(self.Flask)

    @property
    def request(self):
        """Get flask request"""
        return flask.request

    def run(self, port: int = None, debug: bool = False, **kwargs):
        """Run flask app"""
        return self.Flask.run(port=port, debug=debug, **kwargs)
