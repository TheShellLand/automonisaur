import os

from automon.log import Logging


class SwiftConfig:
    OS_USERNAME = os.getenv('OS_USERNAME') or ''
    OS_PASSWORD = os.getenv('OS_PASSWORD') or ''
    OS_AUTH_URL = os.getenv('OS_AUTH_URL') or ''
    OS_PROJECT_ID = os.getenv('OS_PROJECT_ID') or ''
    OS_PROJECT_NAME = os.getenv('OS_PROJECT_NAME') or ''
    OS_USER_DOMAIN_NAME = os.getenv('OS_USER_DOMAIN_NAME') or ''
    OS_PROJECT_DOMAIN_ID = os.getenv('OS_PROJECT_DOMAIN_ID') or ''
    OS_REGION_NAME = os.getenv('OS_REGION_NAME') or 'RegionOne'
    OS_INTERFACE = os.getenv('OS_INTERFACE') or 'public'
    OS_IDENTITY_API_VERSION = os.getenv('OS_IDENTITY_API_VERSION') or '3'
    SWIFTCLIENT_INSECURE = os.getenv('SWIFTCLIENT_INSECURE') or 'True'

    def __init__(self):
        self.log = Logging(name=SwiftConfig.__name__, level=Logging.DEBUG)

        if not self.OS_USERNAME:
            self.log.warn(f'missing OS_USERNAME')
        if not self.OS_PASSWORD:
            self.log.warn(f'missing OS_PASSWORD')
        if not self.OS_AUTH_URL:
            self.log.warn(f'missing OS_AUTH_URL')
        if not self.OS_PROJECT_ID:
            self.log.warn(f'missing OS_PROJECT_ID')
        if not self.OS_PROJECT_NAME:
            self.log.warn(f'missing OS_PROJECT_NAME')
        if not self.OS_USER_DOMAIN_NAME:
            self.log.warn(f'missing OS_USER_DOMAIN_NAME')
        if not self.OS_PROJECT_DOMAIN_ID:
            self.log.warn(f'missing OS_PROJECT_DOMAIN_ID')
        if not self.OS_REGION_NAME:
            self.log.warn(f'missing OS_REGION_NAME')
        if not self.OS_INTERFACE:
            self.log.warn(f'missing OS_INTERFACE')
        if not self.OS_IDENTITY_API_VERSION:
            self.log.warn(f'missing OS_IDENTITY_API_VERSION')
        if not self.SWIFTCLIENT_INSECURE:
            self.log.warn(f'missing SWIFTCLIENT_INSECURE')

    def __eq__(self, other):
        if not isinstance(other, SwiftConfig):
            self.log.warn(f'Not implemented')
            return NotImplemented

        return self.OS_USERNAME == other.OS_USERNAME and \
               self.OS_PASSWORD == other.OS_PASSWORD and \
               self.OS_AUTH_URL == other.OS_AUTH_URL and \
               self.OS_PROJECT_ID == other.OS_PROJECT_ID and \
               self.OS_PROJECT_NAME == other.OS_PROJECT_NAME and \
               self.OS_PROJECT_DOMAIN_ID == other.OS_PROJECT_DOMAIN_ID
