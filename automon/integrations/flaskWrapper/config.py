import os
import hashlib

from automon.helpers.osWrapper import environ


class FlaskConfig(object):

    def __init__(
            self,
            host: str = None,
            port: int = None,
            debug: bool = None,
            **kwargs
    ):
        self.host = host or environ('FLASK_HOST')
        self.port = port or environ('FLASK_PORT')
        self.debug = debug or environ('FLASK_DEBUG')

    @staticmethod
    def javascript_compatibility(app):
        """Javascript expression compatibility

        Required to work with passing args to a flask page
        """

        jinja_options = app.jinja_options.copy()

        jinja_options.update(dict(
            block_start_string='<%',
            block_end_string='%>',
            variable_start_string='%%',
            variable_end_string='%%',
            comment_start_string='<#',
            comment_end_string='#>'
        ))

        return jinja_options

    @staticmethod
    def hash_key(blob):
        """Make a hash key"""
        return hashlib.md5(str(blob).encode()).digest().hex()

    @staticmethod
    def new_secret_key():
        """Create new session key"""
        return os.urandom(16)
