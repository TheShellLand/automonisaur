import flask
from flask import Flask

from automon import log
from automon.integrations.flaskWrapper.config import FlaskConfig

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class FlaskBoilerplate(object):

    def __init__(self, import_name: str = __name__, config: FlaskConfig = None, **kwargs):
        """Wrapper for flask"""

        self.Flask = Flask(import_name=import_name, **kwargs)
        self.config = config or FlaskConfig()

    def __repr__(self):
        return f'{self.Flask}'

    @property
    def flask(self):
        return flask

    @property
    def request(self):
        """Get flask request"""
        return flask.request

    def enable_javascript_compatibility(self):
        """Enable Jinya compatibility for JavaScript"""
        self.Flask = FlaskConfig.javascript_compatibility(self.Flask)

    def run(self, port: int = None, debug: bool = False, **kwargs):
        """Run flask app"""
        return self.Flask.run(port=port, debug=debug, **kwargs)
