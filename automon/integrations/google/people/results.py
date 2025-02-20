from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

from .person import Person

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class ConnectionsResults:
    connections: list
    nextPageToken: str
    nextSyncToken: str
    totalPeople: int
    totalItems: int

    def __init__(self, result: dict):
        """people.connections.list results

        {
          "connections": [
            {
              object (Person)
            }
          ],
          "nextPageToken": string,
          "nextSyncToken": string,
          "totalPeople": integer,
          "totalItems": integer
        }
        """

        self.connections = None
        self.nextPageToken = None
        self.nextSyncToken = None
        self.totalItems = None
        self.totalPeople = None

        self.__dict__.update(result)

        logger.debug(msg=f'{self}')

    def __repr__(self):
        return f'totalPeople: {self.totalPeople}, totalItems: {self.totalItems}, contacts: {len(self.contacts)}'

    def __eq__(self, other):
        if isinstance(other, ConnectionsResults):
            return self.__dict__ == other.__dict__
        return NotImplemented

    @property
    def contacts(self) -> [Person]:
        return [Person(x) for x in self.connections]
