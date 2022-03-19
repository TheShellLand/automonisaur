from automon.log import Logging

from .person import Person

log = Logging(name='PeopleResults', level=Logging.DEBUG)


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

        log.debug(msg=f'{self}')

    def __repr__(self):
        return f'totalPeople: {self.totalPeople}, totalItems: {self.totalItems}, contacts: {len(self.contacts)}'

    def __eq__(self, other):
        if isinstance(other, ConnectionsResults):
            return self.__dict__ == other.__dict__
        return NotImplemented

    @property
    def contacts(self) -> [Person]:
        return [Person(x) for x in self.connections]
