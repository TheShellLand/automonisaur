import os
import hashlib

from flask import Flask


class FlaskConfig(Flask):

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
