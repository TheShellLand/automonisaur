import json

DEBUG = 2


def debug(log: str, level: int = 1):
    if DEBUG == level:
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

    def automon_incident_name(self) -> str:
        if self.DeviceGroup and self.Name:
            incident_name = f'{self.DeviceGroup} :: {self.Name}'.upper()
            debug(f'[PanoramaSecurityRule] :: automon_incident_name :: {incident_name=}', level=2)
            return incident_name
        raise Exception(f'[PanoramaSecurityRule] '
                        f':: automon_incident_name '
                        f':: ERROR '
                        f':: missing {self.DeviceGroup=} {self.Name=}')

    def automon_get_smax_from_description(self) -> list:
        import re

        smax_ids = []

        if self.Description:
            smax = self.Description
            smax = smax.strip()
            smax = smax.upper()

            smax_re = r'[0-9]{7}'
            smax_recompile = re.compile(smax_re)

            smax_ids = smax_recompile.findall(smax)

        debug(f'[PanoramaSecurityRule] :: automon_get_smax_from_description :: {smax_ids=}', level=2)
        return smax_ids

    def update(self, dict):
        self.__dict__.update(dict)
        assert self.DeviceGroup
        assert self.Name
        debug(f'[PanoramaSecurityRule] :: update :: {self.__dict__}', level=3)
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

    def update_rawJSON(self, dict):
        self.rawJSON = json.dumps(dict)
        return self

    def update(self, dict):
        if hasattr(dict, '__dict__'):
            dict = dict.__dict__
        self.__dict__.update(dict)
        debug(f'[Incident] :: update :: {self.__dict__}', level=3)
        debug(f'[Incident] :: update :: done')
        return self

    def to_xsoar(self):
        return self.__dict__

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return json.dumps(self.__dict__)


class IncidentResponse:

    def __init__(self):
        self.Contents = {}

    def __repr__(self):
        return f'{self.__dict__}'

    def __bool__(self):
        if self.data:
            return True
        return False

    def update(self, object: dict):
        try:
            if hasattr(object, '__dict__'):
                object = object.__dict__

            assert type(object) == dict, f'not a dict :: {object=}'

            self.__dict__.update(object)
            if self.Contents:
                data = self.Contents['data']
                if data:
                    self.Contents['data'] = [Incident().update(x) for x in data if x]
            debug(f'[IncidentResponse] :: update :: {self.__dict__}', level=3)
            debug(f'[IncidentResponse] :: update :: done')
            return self
        except Exception as error:
            raise Exception(f'[IncidentResponse] :: update :: ERROR :: {error=}')

    def to_xsoar(self):
        return self.__dict__


class AutomonFirewallRuleIncident(Incident):

    def __init__(self):
        super().__init__()

        self.createInvestigation = True
        self.customFields = {
            'automonfirewallruledevicegroup': None,
            'automonfirewallrulename': None,
            "automonfirewallrulefirstadded": None,
            "automonfirewallrulelastupdated": None,
            'automonfirewallrulelastused': None,
            'automonfirewallruleowneremail': None,
            'automonfirewallruleownerlastcontact': None,
            'automonfirewallrulesmaxids': None,
            'automonfirewallrulesmaxlinks': None,
        }
        self.labels = []
        self.name = None
        self.rawJSON = None
        self.type = 'AUTOMON_FirewallRule'

    def update_from_security_rule(self, security_rule: PanoramaSecurityRule):
        self.name = security_rule.automon_incident_name()
        self.rawJSON = security_rule.to_json()
        self.customFields['automonfirewallruledevicegroup'] = security_rule.DeviceGroup
        self.customFields['automonfirewallrulename'] = security_rule.Name
        debug(f'[AutomonFirewallRuleIncident] '
              f':: update_from_security_rule '
              f':: {security_rule.DeviceGroup} '
              f':: {security_rule.Name}', level=2)
        debug(f'[AutomonFirewallRuleIncident] :: update_from_security_rule :: done')
        return self
