## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from automon.integrations.xsoar.local_testing import *
    # from local_dev.common import *
except:
    pass


class AutomonFirewallRuleIncident(Incident):

    def __init__(self, incident: Incident = None):
        super().__init__()

        self.createInvestigation: bool = True
        self.customFields = dict(
            # security rule
            automonfirewallrulename='',
            automonfirewallruledevicegroup='',

            # security rule metadata
            automonfirewallrulesmaxids=[],
            automonfirewallrulesmaxidscount=None,
            automonfirewallrulesmaxlinks=[],

            automonfirewallrulerawjson='',

            # security rule last hit
            automonfirsthittimestamp='',
            automonhitcount=None,
            automonlasthittimestamp='',
            automonlastreceivetimestamp='',
            automonlastresettimestamp='',
            automonrulecreationtimestamp='',
            automonrulemodificationtimestamp='',

            automonsecurityrulehitcountrawjson=[],

            # smax data
            automonsmaxrawjson=[],

            # smax id lookup
            automonsmaxidrawjson=[],
            automonsmaxpersonrawjson=[],

            # smax person lookup
            automonsmaxarchitectname=[],
            automonsmaxmanagerialcontact=[],
            automonsmaxtechnicalcontact=[],
            automonsmaxexpertassignee=[],

            # smax person emails
            automonsmaxmanagerialcontactemail=[],
            automonsmaxtechnicalcontactemail=[],
            automonsmaxexpertassigneeeamil=[],
        )
        self.labels: list = []
        self.tags: list = []
        self.name: str = None
        self.rawJSON: str = None
        self.type = 'AUTOMON_FirewallRule'
        self.CustomFields: dict = None

        if incident:
            self.update(incident)

    def automon_custom_smax_id_fields(self):
        customFields = self.customFields

        automonsmaxarchitectname = customFields['automonsmaxarchitectname']
        automonsmaxmanagerialcontact = customFields['automonsmaxmanagerialcontact']
        automonsmaxtechnicalcontact = customFields['automonsmaxtechnicalcontact']
        automonsmaxexpertassignee = customFields['automonsmaxexpertassignee']

        debug(f'[AutomonFirewallRuleIncident] :: automon_custom_smax_id_fields :: '
              f'{automonsmaxarchitectname=}', level=3)
        debug(f'[AutomonFirewallRuleIncident] :: automon_custom_smax_id_fields :: '
              f'{automonsmaxmanagerialcontact=}', level=3)
        debug(f'[AutomonFirewallRuleIncident] :: automon_custom_smax_id_fields :: '
              f'{automonsmaxtechnicalcontact=}', level=3)
        debug(f'[AutomonFirewallRuleIncident] :: automon_custom_smax_id_fields :: '
              f'{automonsmaxexpertassignee=}', level=3)

        return dict(
            automonsmaxarchitectname=automonsmaxarchitectname,
            automonsmaxmanagerialcontact=automonsmaxmanagerialcontact,
            automonsmaxtechnicalcontact=automonsmaxtechnicalcontact,
            automonsmaxexpertassignee=automonsmaxexpertassignee,
        )

    def update(self, incident: Incident):
        import json
        # import pandas

        # property update customFields
        customFields = self.customFields.copy()
        customFields.update(incident.customFields)
        self._update(incident)
        self.customFields.update(customFields)

        customFields = self.customFields
        CustomFields = self.CustomFields

        assert type(customFields) == dict
        assert type(CustomFields) == dict

        if not CustomFields:
            return self

        for key in customFields.keys():
            customField = customFields[key]
            debug(f'[AutomonFirewallRuleIncident] :: update :: {key=} {customField=}', level=2)

            try:
                customField = json.loads(customField)
            except:
                continue

            if key in CustomFields:
                CustomField = CustomFields[key]

                debug(f'[AutomonFirewallRuleIncident] :: update :: {key=} {CustomField=}', level=2)

                try:
                    CustomField = json.loads(CustomField)
                except:
                    continue

                if not customField and CustomField:
                    customFields[key] = CustomField

                elif customField and CustomField:
                    assert type(customField) == type(CustomField)

                    if type(customField) == list:
                        customFields[key].extend(CustomField)

                    elif type(customField) == str:
                        customFields[key] = CustomField

                    elif type(customField) == dict:
                        customFields[key] = json.dumps(CustomField, indent=4)

        debug(f'[AutomonFirewallRuleIncident] :: update :: {self.to_json()}', level=2)
        return self

    def update_from_security_rule(self, security_rule: PanoramaSecurityRule):
        self.name = security_rule.automon_incident_name()

        customFields = self.customFields

        customFields['automonfirewallruledevicegroup'] = security_rule.DeviceGroup
        customFields['automonfirewallrulename'] = security_rule.Name
        customFields['automonfirewallrulerawjson'] = security_rule.to_json(indent=4)

        smax_ids = security_rule.automon_get_smax_from_description()
        customFields['automonfirewallrulesmaxids'] = smax_ids
        customFields['automonfirewallrulesmaxidscount'] = len(smax_ids)

        global SMAX_HOST
        if 'SMAX_HOST' not in globals():
            SMAX_HOST = ''

        customFields['automonfirewallrulesmaxlinks'] = [f'{SMAX_HOST}/saw/Request/{x}' for x in smax_ids]

        debug(f'[AutomonFirewallRuleIncident] :: update_from_security_rule :: {self.to_json()}', level=2)
        return self

    def update_from_smax_ticket(self, ticket: SmaxQueryTicketResponse):
        import json

        assert type(ticket) == SmaxQueryTicketResponse

        debug(f'[AutomonFirewallRuleIncident] :: update_from_smax_ticket :: {ticket}', level=2)

        customFields = self.customFields

        ticket_raw = ticket.to_dict()

        automonsmaxrawjson = customFields['automonsmaxrawjson']
        if automonsmaxrawjson:
            if type(automonsmaxrawjson) == str:
                automonsmaxrawjson = json.loads(automonsmaxrawjson)

            assert type(automonsmaxrawjson) == list

            if ticket_raw not in automonsmaxrawjson:
                automonsmaxrawjson.append(ticket_raw)
                automonsmaxrawjson = [x for x in automonsmaxrawjson if type(x) == dict]
            customFields['automonsmaxrawjson'] = automonsmaxrawjson
        else:
            customFields['automonsmaxrawjson'] = [ticket_raw]

        try:
            self.to_json()
        except Exception as error:
            raise Exception(f'ERROR :: {error=} :: {self.__dict__}')

        debug(f'[AutomonFirewallRuleIncident] :: update_from_smax_ticket :: {self.to_json()}', level=2)
        return self

    def update_from_smax_person(
            self,
            Person: SmaxPerson):

        Id = Person.automon_Id
        email = Person.automon_Email

        customFields = self.customFields

        if Id in customFields['automonsmaxmanagerialcontact']:
            if email not in customFields['automonsmaxmanagerialcontactemail']:
                customFields['automonsmaxmanagerialcontactemail'].append(email)

        if Id in customFields['automonsmaxtechnicalcontact']:
            if email not in customFields['automonsmaxtechnicalcontactemail']:
                customFields['automonsmaxtechnicalcontactemail'].append(email)

        debug(f'[AutomonFirewallRuleIncident] :: update_from_smax_person :: {self.to_json()}', level=2)
        return self


class PanoramaRuleHitCount(Dict):

    def __init__(self, device_group: str = None, rule_name: str = None):
        super().__init__()

        self.automon_device_group = device_group
        self.automon_rule_name: str = rule_name

        self.automon_rule_id: str = ''
        self.automon_first_hit_timestamp: str = ''
        self.automon_hit_count: int = 0
        self.automon_last_hit_timestamp: str = ''
        self.automon_last_receive_timestamp: str = ''
        self.automon_last_reset_timestamp: str = ''
        self.automon_rule_creation_timestamp: str = ''
        self.automon_rule_modification_timestamp: str = ''
        self.automon_vsys: str = ''

    def __repr__(self):
        if (self.automon_device_group and self.automon_rule_name and self.automon_vsys and
                self.automon_rule_id and self.automon_last_hit_timestamp):
            last_hit = self.automon_last_hit_timestamp.split('T')[0]
            last_modified = self.automon_rule_modification_timestamp.split('T')[0]
            return (f'{self.automon_device_group} :: {self.automon_rule_name} :: '
                    f'{self.automon_vsys} :: {self.automon_rule_id} :: '
                    f'{last_hit=} :: {last_modified=}')
        return ''

    def __lt__(self, other):
        try:
            A = int(self.__dict__['last-hit-timestamp'])
            B = int(other.__dict__['last-hit-timestamp'])
            if A < B:
                return True
        except:
            pass
        return False

    def update(self, update: dict):
        import json
        import datetime

        assert type(update) == dict, f'{update=}'

        self._update(update)

        if '@name' in self.__dict__:
            self.automon_rule_id = self.__dict__['@name'].split('/')[1]
            debug(f'[PanoramaRuleHitCount] :: update :: {self.automon_rule_id=}', level=2)

        if self.__dict__['first-hit-timestamp']:
            self.automon_first_hit_timestamp = str(
                datetime.datetime.fromtimestamp(int(self.__dict__['first-hit-timestamp'])).strftime(
                    "%Y-%m-%dT%H:%M:%S"))
            debug(f'[PanoramaRuleHitCount] :: update :: {self.automon_first_hit_timestamp=}', level=2)

        if self.__dict__['hit-count']:
            self.automon_hit_count = int(self.__dict__['hit-count'])
            debug(f'[PanoramaRuleHitCount] :: update :: {self.automon_hit_count=}', level=2)

        if self.__dict__['last-hit-timestamp']:
            self.automon_last_hit_timestamp = str(
                datetime.datetime.fromtimestamp(int(self.__dict__['last-hit-timestamp'])).strftime("%Y-%m-%dT%H:%M:%S"))
            debug(f'[PanoramaRuleHitCount] :: update :: {self.automon_last_hit_timestamp=}', level=2)

        if self.__dict__['last-receive-timestamp']:
            self.automon_last_receive_timestamp = str(
                datetime.datetime.fromtimestamp(int(self.__dict__['last-receive-timestamp'])).strftime(
                    "%Y-%m-%dT%H:%M:%S"))
            debug(f'[PanoramaRuleHitCount] :: update :: {self.automon_last_receive_timestamp=}', level=2)

        if self.__dict__['last-reset-timestamp']:
            self.automon_last_reset_timestamp = str(
                datetime.datetime.fromtimestamp(int(self.__dict__['last-reset-timestamp'])).strftime(
                    "%Y-%m-%dT%H:%M:%S"))
            debug(f'[PanoramaRuleHitCount] :: update :: {self.automon_last_reset_timestamp=}', level=2)

        if self.__dict__['rule-creation-timestamp']:
            self.automon_rule_creation_timestamp = str(
                datetime.datetime.fromtimestamp(int(self.__dict__['rule-creation-timestamp'])).strftime(
                    "%Y-%m-%dT%H:%M:%S"))
            debug(f'[PanoramaRuleHitCount] :: update :: {self.automon_rule_creation_timestamp=}', level=2)

        if self.__dict__['rule-modification-timestamp']:
            self.automon_rule_modification_timestamp = str(
                datetime.datetime.fromtimestamp(int(self.__dict__['rule-modification-timestamp'])).strftime(
                    "%Y-%m-%dT%H:%M:%S"))
            debug(f'[PanoramaRuleHitCount] :: update :: {self.automon_rule_modification_timestamp=}', level=2)

        if '@name' in self.__dict__:
            self.automon_vsys = self.__dict__['@name'].split('/')[-1]
            debug(f'[PanoramaRuleHitCount] :: update :: {self.automon_vsys=}', level=2)

        debug(f'[PanoramaRuleHitCount] :: update :: {self.to_json()=}', level=2)
        debug(f'[PanoramaRuleHitCount] :: update :: {self=}', level=2)
        return self

    def to_json(self, indent: int = None):
        try:
            return self._to_json(indent)
        except Exception as error:
            raise Exception(f'ERROR :: {error} :: {self.__dict__}')


class PanoramaSecurityRule(Dict):

    def __init__(self, update: dict | str = None):
        super().__init__()

        self.DeviceGroup = None
        self.Name = None
        self.Description = None

        self.automon_rulebase = None

        if update:
            self._update(update)
            assert self.DeviceGroup
            assert self.Name

    def __repr__(self):
        return f'{self.DeviceGroup} :: {self.Name} :: {self.automon_rulebase}'

    def __bool__(self):
        if self.Name and self.DeviceGroup:
            return True
        return False

    def __eq__(self, other):
        if not type(other) == PanoramaSecurityRule:
            raise Exception(f'[PanoramaSecurityRule] :: __eq__ :: ERROR :: {type(other)=}')

        if self.Name == other.Name:
            if self.DeviceGroup == other.DeviceGroup:
                return True
        return False

    def automon_incident_name(self) -> str:
        if self.DeviceGroup and self.Name and self.automon_rulebase:
            assert f'{self.automon_rulebase}'.lower() == 'pre-rulebase' or 'post-rulebase'

            incident_name = f'{self.DeviceGroup} :: {self.Name} :: {self.automon_rulebase}'
            debug(f'[PanoramaSecurityRule] :: automon_incident_name :: {incident_name=}', level=4)
            return incident_name

        raise Exception(f'[PanoramaSecurityRule] :: automon_incident_name :: ERROR :: '
                        f'missing {self.DeviceGroup=} {self.Name=} {self.automon_rulebase=}')

    def automon_get_smax_from_description(self) -> list:
        import re

        smax_tickets = []

        Description = self.Description

        if Description:
            smax = Description
            smax = smax.strip()
            smax = smax.upper()

            smax_re = r'[0-9]{6,7}'
            smax_recompile = re.compile(smax_re)

            smax_tickets = smax_recompile.findall(smax)

            if not smax_tickets:
                debug(f'[PanoramaSecurityRule] :: automon_get_smax_from_description :: ERROR :: '
                      f'no smax ticket :: {Description=}')

        debug(f'[PanoramaSecurityRule] :: automon_get_smax_from_description :: {Description=}', level=3)
        debug(f'[PanoramaSecurityRule] :: automon_get_smax_from_description :: {smax_tickets=}', level=3)
        return smax_tickets


class PanoramaResponse(Dict):

    def __init__(self, update: dict | str = None):
        super().__init__()
        self.Brand: str = None
        self.Contents: dict = None
        self.Category: str = None
        self.ModuleName: str = None

        if update:
            self._update(update)

    def __repr__(self):
        return f'{self.Brand} :: {self.Category} :: {self.ModuleName}'

    def automon_get_rule_hit_count(self) -> list[PanoramaRuleHitCount]:

        rule_hit_counts = []

        Contents = self.Contents
        try:
            assert type(
                Contents) == dict, f"[PanoramaResponse] :: automon_get_rule_hit_count :: {Contents=} \n\n {self.to_dict()}"
        except Exception as error:
            debug_error(f"[PanoramaResponse] :: automon_get_rule_hit_count :: {Contents=} \n\n {self.to_dict()}")
            return []

        debug(f'[PanoramaResponse] :: automon_get_rule_hit_count :: {Contents=}', level=4)

        _response = None
        if Contents:
            if 'response' in Contents:
                _response = Contents.get('response')

        _result = None
        if _response:
            _status = _response.get('@status')
            _result = _response.get('result')

            debug(f'[PanoramaResponse] :: automon_get_rule_hit_count :: {_status=}', level=4)

        _rule_hit_count = None
        if _result:
            if 'rule-hit-count' in _result:
                _rule_hit_count = _result.get('rule-hit-count')

        device_group = None
        if _rule_hit_count:
            if 'device-group' in _rule_hit_count:
                device_group = _rule_hit_count.get('device-group')

                assert device_group

        rules = None
        if device_group:
            rules = device_group['entry']['rule-base']['entry']['rules']
            device_group = str(device_group['entry']['@name'])

            assert rules
            assert device_group

        rule_name = None
        vsys = None
        if rules:
            vsys = rules['entry']['device-vsys']
            rule_name = str(rules['entry']['@name'])

            assert rule_name

        entries = None
        if vsys:
            entries = vsys['entry']

            assert entries

        if entries:
            if type(entries) == dict:
                entries = [entries]

            for entry in entries:
                debug(f'[PanoramaResponse] :: automon_get_rule_hit_count :: {entry=}', level=2)

                assert type(entry) == dict, f'{entry=} :: {entries=}'

                entry = PanoramaRuleHitCount(device_group=device_group, rule_name=rule_name).update(entry)

                rule_hit_counts.append(entry)

        debug(f'[PanoramaResponse] :: automon_get_rule_hit_count :: {len(rule_hit_counts)} entries', level=2)
        return rule_hit_counts
