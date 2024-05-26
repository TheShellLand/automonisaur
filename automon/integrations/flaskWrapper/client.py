from automon import logging

from .app import app
from .config import FlaskConfig

log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)


class FlaskClient(object):

    def __init__(
            self,
            host: str = None,
            port: int = None,
            debug: bool = True,
            config: FlaskConfig = None,
            **kwargs
    ):
        self.config = config or FlaskConfig(
            host=host,
            port=port,
            debug=debug,
            **kwargs
        )
        self.host = self.config.host
        self.port = self.config.port
        self.debug = self.config.debug

        self.app = app

    def run(self, **kwargs):
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug,
            **kwargs
        )
