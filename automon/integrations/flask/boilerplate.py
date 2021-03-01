from flask import Flask

from automon.log.logger import Logging
from automon.integrations.flask.config import FlaskConfig


class FlaskBoilerplate:

    def __init__(self, flask_name=__name__):
        self._log = Logging(FlaskBoilerplate.__name__, Logging.DEBUG)

        self.app = Flask(flask_name)
        self.app = FlaskConfig.javascript_compatibility(self.app)
