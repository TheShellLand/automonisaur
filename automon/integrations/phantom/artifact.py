from automon import Logging

from .common import Scaffolding

log = Logging('Artifact', level=Logging.CRITICAL)


class Artifact(Scaffolding):
    def __init__(self, artifact: dict):
        self.__dict__.update(artifact)
