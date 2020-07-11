import os

from automon.helpers.sanitation import Sanitation as S


class Neo4jConfig:
    def __init__(self):
        self.user = os.getenv('NEO4J_USER')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.hosts = S.list_from_string(os.getenv('NEO4J_SERVERS'))
