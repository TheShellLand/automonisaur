## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from automon.integrations.xsoar.local_testing import *
    from automon.integrations.xsoar.demistoWrapper import *
    # from local_dev.common import *
except:
    pass


class Incident(Dict):

    def __init__(self, update: dict | str = None):
        super().__init__()

        self.createInvestigation = True
        self.customFields = {}
        self.details = None
        self.id = None
        self.labels = []
        self.name = None
        self.rawJSON = None
        self.severity = 'Unknown'
        self.type = None

        self.CustomFields = {}

        if update:
            self._update(update)

    def __repr__(self):
        id = self.id
        name = self.name

        if id:
            global XSOAR_HOST
            if 'XSOAR_HOST' not in globals():
                XSOAR_HOST = ''
            return f'{id} :: {name} :: {XSOAR_HOST}/#/incident/{id}'

        return f'{name=}'

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

    def update_rawJSON(self, dict_: dict):
        import json
        self.rawJSON = json.dumps(dict_)
        return self

    def to_create_incident(self):
        return self.__dict__

    def to_update_incident(self) -> dict:
        """
        since xsoar has special fields, you have to remove them

        it's better to remove them than to add a growing list of custom fields

        I hate it, but it is what it is. xsoar sucks.
        """
        import json

        stupid_xsoar_fields = [
            'severity',
            'account',
            'activated',
            'attachment',
            'autime',
            'cacheVersn',
            'canvases',
            'category',
            'closeNotes',
            'closeReason',
            'closed',
            'closingUserId',
            'created',
            'dbotCurrentDirtyFields',
            'dbotDirtyFields',
            'dbotMirrorDirection',
            'dbotMirrorId',
            'dbotMirrorInstance',
            'dbotMirrorLastSync',
            'dbotMirrorTags',
            'droppedCount',
            'dueDate',
            'feedBased',
            # 'investigationId',
            'isDebug',
            'isPlayground',
            'lastJobRunTime',
            'lastOpen',
            'linkedCount',
            'linkedIncidents',
            'modified',
            'notifyTime',
            'occurred',
            'openDuration',
            # 'owner',
            'parent',
            'phase',
            # 'playbookId',
            'rawCategory',
            'rawCloseReason',
            'rawName',
            'rawPhase',
            'rawType',
            'reason',
            'reminder',
            'runStatus',
            'sizeInBytes',
            'sla',
            'sortValues',
            'sourceBrand',
            'sourceInstance',
            'status',
            'version',
            'details',
            'accumulatedPause',
            'breachTriggered',
            'endDate',
            'lastPauseDate',
            'slaStatus',
            'startDate',
            'totalDuration',
            'columnheader1',
        ]

        update_incident = self._flatten()

        for key in list(update_incident):
            if key in stupid_xsoar_fields:
                del update_incident[key]

        debug(f'[Incident] :: to_update_incident :: update_incident :: {json.dumps(update_incident)}', level=3)
        return update_incident

    def to_xsoar(self):
        return self.__dict__


class IncidentResponse(Dict):

    def __init__(self):
        super().__init__()

    def to_xsoar(self):
        return self.__dict__


class IncidentCreateResponse(IncidentResponse):

    def __init__(self):
        super().__init__()
        self.EntryContext = {}
        self.Metadata = {}

    def __repr__(self):
        return f'{self.automon_CreatedIncidentID()}'

    def automon_CreatedIncidentID(self) -> str:
        if self.EntryContext:
            if 'CreatedIncidentID' in self.EntryContext.keys():
                CreatedIncidentID = self.EntryContext['CreatedIncidentID']
                debug(f'[IncidentCreateResponse] :: automon_CreatedIncidentID :: {CreatedIncidentID=}', level=3)
                return CreatedIncidentID
        return ''

    def automon_parentContent(self) -> str:
        if self.Metadata:
            if 'parentContent' in self.Metadata.keys():
                parentContent = self.Metadata.get('parentContent')
                debug(f'[IncidentCreateResponse] :: automon_parentContent :: {parentContent=}', level=3)
                return parentContent
        return ''

    def update(self, dict_: dict):
        if hasattr(dict_, '__dict__'):
            dict_ = dict_.__dict__

        assert type(dict_) == dict, f'not a dict :: {dict_=}'

        self.__dict__.update(dict_)

        debug(f'[IncidentCreateResponse] :: update :: {self.to_json()=}', level=4)
        debug(f'[IncidentCreateResponse] :: update :: {self=}', level=3)
        return self


class IncidentUpdateResponse(IncidentResponse):

    def __init__(self):
        super().__init__()
        self.Metadata = {}

    def __repr__(self):
        if self.Metadata:
            id = self.Metadata["id"]
            investigationId = self.Metadata["investigationId"]
            parentId = self.Metadata["parentId"]

            return f'{id=} :: {investigationId=} :: {parentId=}'
        return f''

    def update(self, dict_: dict):
        if hasattr(dict_, '__dict__'):
            dict_ = dict_.__dict__

        self.__dict__.update(dict_)
        debug(f'[IncidentUpdateResponse] :: update :: {self.to_json()}', level=2)

        return self


class IncidentSearchResponse(IncidentResponse):

    def __init__(self):
        super().__init__()
        self.Contents = {}

    def __repr__(self):
        return f'{self.automon_total()} search results'

    def __bool__(self):
        if self.automon_data():
            return True
        return False

    def automon_data(self) -> [Incident]:
        import json

        if self.Contents:
            debug(f'[IncidentSearchResponse] :: automon_data :: {json.dumps(self.Contents)=}', level=3)

            if 'data' in self.Contents:
                data = self.Contents['data']
                if data:
                    debug(f'[IncidentSearchResponse] :: automon_data :: {json.dumps(data)=}', level=3)
                    return data
        return []

    def automon_incidents(self) -> [Incident]:
        incidents = self.automon_data()
        incidents = [Incident().update(x) for x in incidents if x]
        debug(f'[IncidentSearchResponse] :: automon_incidents :: {incidents}', level=4)
        return incidents

    def automon_total(self) -> str:
        if self.Contents:
            if 'total' in self.Contents:
                total = self.Contents['total']
                if type(total) is int:
                    debug(f'[IncidentSearchResponse] :: total :: {total}', level=4)
                    return total
        return ''

    def update(self, response: dict):
        if hasattr(response, '__dict__'):
            response = response.__dict__

        assert type(response) == dict, f'not a dict :: {response=}'

        self.__dict__.update(response)

        debug(f'[IncidentSearchResponse] :: update :: {self.to_json()}', level=4)
        debug(f'[IncidentSearchResponse] :: update :: {self}', level=2)
        return self


class GenericSearchResponse(IncidentSearchResponse):

    def __init__(self):
        super().__init__()
        pass

    def __repr__(self):
        try:
            return f'search results :: {len(self.Contents["total"])}'
        except:
            return f''

    def update(self, object: dict):
        self.__dict__.update(object)
        return self

    def to_dict(self):
        return self.__dict__
