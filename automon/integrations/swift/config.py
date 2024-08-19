import os

from automon import log
from automon import environ

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class SwiftConfig:
    OPENSTACK_USERNAME = environ('OPENSTACK_USERNAME', '')
    OPENSTACK_PASSWORD = environ('OPENSTACK_PASSWORD', '')
    OPENSTACK_AUTH_URL = environ('OPENSTACK_AUTH_URL', '')
    OPENSTACK_PROJECT_ID = environ('OPENSTACK_PROJECT_ID', '')
    OPENSTACK_PROJECT_NAME = environ('OPENSTACK_PROJECT_NAME', '')
    OPENSTACK_USER_DOMAIN_NAME = environ('OPENSTACK_USER_DOMAIN_NAME', '')
    OPENSTACK_PROJECT_DOMAIN_ID = environ('OPENSTACK_PROJECT_DOMAIN_ID', '')
    OPENSTACK_REGION_NAME = environ('OPENSTACK_REGION_NAME', 'RegionOne')
    OPENSTACK_INTERFACE = environ('OPENSTACK_INTERFACE', 'public')
    OPENSTACK_IDENTITY_API_VERSION = environ('OPENSTACK_IDENTITY_API_VERSION', 3)
    SWIFTCLIENT_INSECURE = environ('SWIFTCLIENT_INSECURE', True)

    def __init__(self):
        pass

    def is_ready(self):
        if not self.OPENSTACK_USERNAME:
            logger.error(f'missing OPENSTACK_USERNAME')
            return False
        if not self.OPENSTACK_PASSWORD:
            logger.error(f'missing OPENSTACK_PASSWORD')
            return False
        if not self.OPENSTACK_AUTH_URL:
            logger.error(f'missing OPENSTACK_AUTH_URL')
            return False
        if not self.OPENSTACK_PROJECT_ID:
            logger.error(f'missing OPENSTACK_PROJECT_ID')
            return False
        if not self.OPENSTACK_PROJECT_NAME:
            logger.error(f'missing OPENSTACK_PROJECT_NAME')
            return False
        if not self.OPENSTACK_USER_DOMAIN_NAME:
            logger.error(f'missing OPENSTACK_USER_DOMAIN_NAME')
            return False
        if not self.OPENSTACK_PROJECT_DOMAIN_ID:
            logger.error(f'missing OPENSTACK_PROJECT_DOMAIN_ID')
            return False
        if not self.OPENSTACK_REGION_NAME:
            logger.error(f'missing OPENSTACK_REGION_NAME')
            return False
        if not self.OPENSTACK_INTERFACE:
            logger.error(f'missing OPENSTACK_INTERFACE')
            return False
        if not self.OPENSTACK_IDENTITY_API_VERSION:
            logger.error(f'missing OPENSTACK_IDENTITY_API_VERSION')
            return False
        if not self.SWIFTCLIENT_INSECURE:
            logger.error(f'missing SWIFTCLIENT_INSECURE')
            return False

        return True

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
