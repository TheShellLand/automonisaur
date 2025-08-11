import json

DEBUG = 2


def debug(log: str, level: int = 1):
    if level <= DEBUG:
        print(log)


def debug_error(log: str, level: int = 1):
    import traceback
    traceback.print_exc()
    if DEBUG == level:
        print(log)


class PanoramaSecurityRule:

    def __init__(self):
        self.DeviceGroup = None
        self.Name = None
        self.Description = None

    def __repr__(self):
        return f'{self.DeviceGroup} :: {self.Name}'

    def __bool__(self):
        if self.__dict__:
            return True
        return False

    def __eq__(self, other):
        if self.Name == other.Name:
            if self.DeviceGroup == other.DeviceGroup:
                return True

        return False

    def automon_incident_name(self) -> str:
        if self.DeviceGroup and self.Name:
            incident_name = f'{self.DeviceGroup} :: {self.Name}'.upper()
            debug(f'[PanoramaSecurityRule] :: automon_incident_name :: {incident_name=}', level=4)
            return incident_name
        raise Exception(f'[PanoramaSecurityRule] '
                        f':: automon_incident_name '
                        f':: ERROR :: missing {self.DeviceGroup=} {self.Name=}')

    def automon_get_smax_from_description(self) -> str:
        import re

        smax_ids = []

        if self.Description:
            smax = self.Description
            smax = smax.strip()
            smax = smax.upper()

            smax_re = r'[0-9]{7}'
            smax_recompile = re.compile(smax_re)

            smax_ids = smax_recompile.findall(smax)

        debug(f'[PanoramaSecurityRule] :: automon_get_smax_from_description :: {smax_ids=}', level=4)
        return ' '.join(smax_ids)

    def update(self, dict):
        self.__dict__.update(dict)
        assert self.DeviceGroup
        assert self.Name
        debug(f'[PanoramaSecurityRule] :: update :: {self.__dict__}', level=4)
        debug(f'[PanoramaSecurityRule] :: update :: done')
        return self

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        import json
        return json.dumps(self.__dict__)


class Incident:

    def __init__(self):
        self.createInvestigation = True
        self.customFields = {}
        self.details = None
        self.id = None
        self.labels = []
        self.name = None
        self.rawJSON = None
        self.severity = 'Unknown'
        self.type = None

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

    def update(self, object: dict):
        if hasattr(object, '__dict__'):
            object = object.__dict__
        self.__dict__.update(object)
        debug(f'[Incident] :: update :: {self.__dict__}', level=4)
        debug(f'[Incident] :: update :: done')
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

            debug(f'[IncidentCreateResponse] :: update :: {self.__dict__}', level=4)
            debug(f'[IncidentCreateResponse] :: update :: done')
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
                    self.Contents['data'] = [Incident().update(x) for x in data if x]
            debug(f'[IncidentSearchResponse] :: update :: {self.__dict__}', level=4)
            debug(f'[IncidentSearchResponse] :: update :: done')
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


class AutomonFirewallRuleIncident(Incident):

    def __init__(self):
        super().__init__()

        self.createInvestigation = True
        self.customFields = {
            'automonfirewallruledevicegroup': None,
            "automonfirewallrulefirstadded": None,
            "automonfirewallrulelastupdated": None,
            'automonfirewallrulelastused': None,
            'automonfirewallrulename': None,
            'automonfirewallruleowneremail': None,
            'automonfirewallruleownerlastcontact': None,
            'automonfirewallrulerawjson': None,
            'automonfirewallrulesmaxids': None,
            'automonfirewallrulesmaxlinks': None,
        }
        self.labels = []
        self.name = None
        self.rawJSON = None
        self.type = 'AUTOMON_FirewallRule'
        self.CustomFields = None

    def update_from_security_rule(self, security_rule: PanoramaSecurityRule):
        self.name = security_rule.automon_incident_name()
        self.rawJSON = security_rule.to_json()
        self.customFields['automonfirewallruledevicegroup'] = security_rule.DeviceGroup
        self.customFields['automonfirewallrulename'] = security_rule.Name
        self.customFields['automonfirewallrulerawjson'] = self.rawJSON
        self.customFields['automonfirewallrulesmaxids'] = security_rule.automon_get_smax_from_description()
        debug(f'[AutomonFirewallRuleIncident] :: update_from_security_rule :: {security_rule=}', level=4)
        debug(f'[AutomonFirewallRuleIncident] :: update_from_security_rule :: done')

        self.CustomFields = self.customFields

        return self
