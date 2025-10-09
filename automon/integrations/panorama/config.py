from automon.helpers.osWrapper import environ


class PanoramaConfig(object):

    def __init__(
            self,
            panorama_host: str = None,
            panorama_api_key: str = None
    ):
        self.PANORAMA_HOST: str = panorama_host or environ(f'PANORAMA_HOST')
        self.PANORAMA_API_KEY: str = panorama_api_key or environ(f'PANORAMA_API_KEY')

    def auth_header(self) -> dict:
        if self.PANORAMA_API_KEY:
            return dict(
                Authorization=f'Basic {self.PANORAMA_API_KEY}'
            )

        raise Exception(f'PanoramaConfig :: ERROR :: missing PANORAMA_API_KEY')

    @property
    def is_ready(self) -> bool:
        if self.PANORAMA_HOST and self.PANORAMA_API_KEY:
            return True
        return False
