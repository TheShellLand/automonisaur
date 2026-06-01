from automon.helpers.debug import debug_exception

from .incident import Incident


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
            return incident_name

        raise debug_exception(locals(), 'no incident name')

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

        return ' '.join(smax_ids)

    def update(self, dict):
        self.__dict__.update(dict)
        assert self.DeviceGroup
        assert self.Name
        return self

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        import json
        return json.dumps(self.__dict__)


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

        self.CustomFields = self.customFields

        return self
