class TACUTeleporterConfig(object):

    def __init__(self):
        self.TACU_TELEPORTER_ENDPOINT: str = 'api.teleporter01.org'
        self.TACU_TELEPORTER_ENDPOINT_PORT: int = 443
        self.TACU_TELEPORTER_TOKEN: str = None

    def is_ready(self) -> bool:
        if self.TACU_TELEPORTER_ENDPOINT and self.TACU_TELEPORTER_ENDPOINT_PORT and self.TACU_TELEPORTER_TOKEN:
            return True
        return False
