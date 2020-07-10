import os

from automon.helpers.sanitation import Sanitation


class Neo4jConfig:
    def __init__(self):
        self.user = os.getenv('NEO4J_USER')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.servers = []

        servers = os.getenv('NEO4J_SERVERS')

        if servers:
            if ',' in servers:
                servers = servers.split(',')
            elif ' ' in servers:
                servers = servers.split(' ')

            for server in servers:
                server = Sanitation.no_quotes(server)
                server = Sanitation.no_spaces(server)
                self.servers.append(server)
