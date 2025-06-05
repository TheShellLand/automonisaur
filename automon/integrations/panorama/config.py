import automon.helpers.osWrapper


class PanoramaConfig(object):

    def __init__(
            self,
            panorama_host: str = None,
            panorama_api_key: str = None
    ):
        self.PANORAMA_HOST: str = panorama_host or automon.helpers.osWrapper.environ(f'PANORAMA_HOST')
        self.PANORAMA_API_KEY: str = panorama_api_key or automon.helpers.osWrapper.environ(f'PANORAMA_API_KEY')

    def auth_header(self) -> dict:
        if self.PANORAMA_API_KEY:
            return dict(
                Authorization=f'Basic {self.PANORAMA_API_KEY}'
            )

        raise Exception(f'PanoramaConfig :: ERROR :: missing PANORAMA_API_KEY')
