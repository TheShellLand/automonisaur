import json

from automon import DictHelper


class Incident(DictHelper):

    def __init__(self, incident: dict = None):
        self.createInvestigation = True
        self.customFields = {}
        self.details = None
        self.id = None
        self.labels = []
        self.name = None
        self.rawJSON = None
        self.severity = 'Unknown'
        self.type = None

        super().__init__(incident)

    def __repr__(self):
        return f'{self.id} :: {self.name} :: {self.type}'

    def __bool__(self):
        if self.id or self.name or self.type:
            return True
        return False

    def __eq__(self, other):
        if self.id == other.id:
            return True

        if self.name == other.name:
            return True

        return False

    def update_rawJSON(self, object: dict):
        self.rawJSON = json.dumps(object)
        return self

    def to_xsoar(self):
        return self.__dict__

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return json.dumps(self.__dict__)


class IncidentCreateResponse:

    def __init__(self):
        self.EntryContext = {}
        self.Metadata = {}

    def __repr__(self):
        if self.EntryContext:
            return f'{self.automon_CreatedIncidentID()}'
        return ''

    def automon_CreatedIncidentID(self) -> str:
        if self.EntryContext:
            if 'CreatedIncidentID' in self.EntryContext.keys():
                return self.EntryContext['CreatedIncidentID']
        return ''

    def automon_parentContent(self) -> str:
        if self.Metadata:
            if 'parentContent' in self.Metadata.keys():
                return self.Metadata.get('parentContent')
        return ''

    def update(self, object: dict):
        try:
            if hasattr(object, '__dict__'):
                object = object.__dict__

            assert type(object) == dict, f'not a dict :: {object=}'

            self.__dict__.update(object)

            return self

        except Exception as error:
            raise Exception(f'[IncidentCreateResponse] :: update :: ERROR :: {error=}')


class IncidentSearchResponse:

    def __init__(self):
        self.Contents = {}

    def __repr__(self):
        return f'{len(self.data())} search results'

    def __bool__(self):
        if self.data():
            return True
        return False

    def data(self) -> list:
        if self.Contents:
            if 'data' in self.Contents.keys():
                data = self.Contents.get('data')
                assert type(data) == list
                return data
        return []

    def update(self, object: dict):
        try:
            if hasattr(object, '__dict__'):
                object = object.__dict__

            assert type(object) == dict, f'not a dict :: {object=}'

            self.__dict__.update(object)
            if self.Contents:
                data = self.Contents.get('data')
                if data:
                    self.Contents['data'] = [Incident(x) for x in data if x]
            return self
        except Exception as error:
            raise Exception(f'[IncidentSearchResponse] :: update :: ERROR :: {error=}')

    def to_xsoar(self):
        return self.__dict__


class IncidentUpdateResponse:

    def __init__(self):
        self.Metadata = {}

    def __repr__(self):
        if self.Metadata:
            id = self.Metadata["id"]
            investigationId = self.Metadata["investigationId"]
            parentId = self.Metadata["parentId"]

            return f'{id=} :: {investigationId=} :: {parentId=}'
        return f''

    def update(self, object: dict):
        self.__dict__.update(object)
        return self
