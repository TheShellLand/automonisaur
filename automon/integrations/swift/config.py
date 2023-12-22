import os

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class SwiftConfig:
    OPENSTACK_USERNAME = os.getenv('OPENSTACK_USERNAME') or ''
    OPENSTACK_PASSWORD = os.getenv('OPENSTACK_PASSWORD') or ''
    OPENSTACK_AUTH_URL = os.getenv('OPENSTACK_AUTH_URL') or ''
    OPENSTACK_PROJECT_ID = os.getenv('OPENSTACK_PROJECT_ID') or ''
    OPENSTACK_PROJECT_NAME = os.getenv('OPENSTACK_PROJECT_NAME') or ''
    OPENSTACK_USER_DOMAIN_NAME = os.getenv('OPENSTACK_USER_DOMAIN_NAME') or ''
    OPENSTACK_PROJECT_DOMAIN_ID = os.getenv('OPENSTACK_PROJECT_DOMAIN_ID') or ''
    OPENSTACK_REGION_NAME = os.getenv('OPENSTACK_REGION_NAME') or 'RegionOne'
    OPENSTACK_INTERFACE = os.getenv('OPENSTACK_INTERFACE') or 'public'
    OPENSTACK_IDENTITY_API_VERSION = os.getenv('OPENSTACK_IDENTITY_API_VERSION') or '3'
    SWIFTCLIENT_INSECURE = os.getenv('SWIFTCLIENT_INSECURE') or 'True'

    def __init__(self):

        if not self.OPENSTACK_USERNAME:
            logger.warning(f'missing OPENSTACK_USERNAME')
        if not self.OPENSTACK_PASSWORD:
            logger.warning(f'missing OPENSTACK_PASSWORD')
        if not self.OPENSTACK_AUTH_URL:
            logger.warning(f'missing OPENSTACK_AUTH_URL')
        if not self.OPENSTACK_PROJECT_ID:
            logger.warning(f'missing OPENSTACK_PROJECT_ID')
        if not self.OPENSTACK_PROJECT_NAME:
            logger.warning(f'missing OPENSTACK_PROJECT_NAME')
        if not self.OPENSTACK_USER_DOMAIN_NAME:
            logger.warning(f'missing OPENSTACK_USER_DOMAIN_NAME')
        if not self.OPENSTACK_PROJECT_DOMAIN_ID:
            logger.warning(f'missing OPENSTACK_PROJECT_DOMAIN_ID')
        if not self.OPENSTACK_REGION_NAME:
            logger.warning(f'missing OPENSTACK_REGION_NAME')
        if not self.OPENSTACK_INTERFACE:
            logger.warning(f'missing OPENSTACK_INTERFACE')
        if not self.OPENSTACK_IDENTITY_API_VERSION:
            logger.warning(f'missing OPENSTACK_IDENTITY_API_VERSION')
        if not self.SWIFTCLIENT_INSECURE:
            logger.warning(f'missing SWIFTCLIENT_INSECURE')

    def __eq__(self, other):
        if not isinstance(other, SwiftConfig):
            logger.warning(f'Not implemented')
            return NotImplemented

        return self.OPENSTACK_USERNAME == other.OPENSTACK_USERNAME and \
            self.OPENSTACK_PASSWORD == other.OPENSTACK_PASSWORD and \
            self.OPENSTACK_AUTH_URL == other.OPENSTACK_AUTH_URL and \
            self.OPENSTACK_PROJECT_ID == other.OPENSTACK_PROJECT_ID and \
            self.OPENSTACK_PROJECT_NAME == other.OPENSTACK_PROJECT_NAME and \
            self.OPENSTACK_PROJECT_DOMAIN_ID == other.OPENSTACK_PROJECT_DOMAIN_ID
