## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from automon.integrations.xsoar.local_testing import *
    from automon.integrations.xsoar.demistoWrapper.funcs import *
    # from local_dev.common import *
except:
    pass


def executeCommand_panos_get_last_hit(
        security_rule: PanoramaSecurityRule) -> list[PanoramaResponse]:
    """get security rule last hit and update its incidents"""
    import json

    rule_name = security_rule.Name
    device_group = security_rule.DeviceGroup
    rulebase = security_rule.automon_rulebase.lower()

    command = 'pan-os'

    cmd = (
        f'<show>'
        f'<rule-hit-count>'
        f'<device-group>'
        f'<entry name="{device_group}">'
        f'<{rulebase}>'
        f'<entry name="security">'
        f'<rules>'
        f'<rule-name>'
        f'<entry name="{rule_name}"/>'
        f'</rule-name>'
        f'</rules>'
        f'</entry>'
        f'</{rulebase}>'
        f'</entry>'
        f'</device-group>'
        f'</rule-hit-count>'
        f'</show>'
    )

    command_args = {
        'type': 'op',
        'action': 'show',
        'cmd': cmd
    }

    print_command(command, command_args)

    response = demisto.executeCommand('pan-os', command_args)

    if response:
        assert isinstance(response, list), f"ERROR :: {response=}"
        assert isinstance(response[0], dict), f"ERROR :: {response=} :: {print_command(command, command_args)}"

    debug(f'[firewall_get_security_rule_last_hit] :: response :: {json.dumps(response)}', level=4)
    response = [PanoramaResponse(x) for x in response]
    debug(f'[firewall_get_security_rule_last_hit] :: response :: {response}', level=2)
    return response


def update_incidents_with_last_hit(
        incident: AutomonFirewallRuleIncident,
        hits: list[PanoramaRuleHitCount]
) -> AutomonFirewallRuleIncident:
    hits.sort()

    for hit in hits:
        incident.customFields['automonfirsthittimestamp'] = hit.automon_first_hit_timestamp
        incident.customFields['automonhitcount'] = hit.automon_hit_count
        incident.customFields['automonlasthittimestamp'] = hit.automon_last_hit_timestamp
        incident.customFields['automonlastreceivetimestamp'] = hit.automon_last_receive_timestamp
        incident.customFields['automonlastresettimestamp'] = hit.automon_last_reset_timestamp
        incident.customFields['automonrulecreationtimestamp'] = hit.automon_rule_creation_timestamp
        incident.customFields['automonrulemodificationtimestamp'] = hit.automon_rule_modification_timestamp

        # incident.customFields['automonsecurityrulehitcountrawjson'].append(hit.to_dict())

        break

    # automonsecurityrulehitcountrawjson = incident.customFields['automonsecurityrulehitcountrawjson']
    # automonsecurityrulehitcountrawjson = [x for x in automonsecurityrulehitcountrawjson if type(x) == dict]
    # incident.customFields['automonsecurityrulehitcountrawjson'] = automonsecurityrulehitcountrawjson

    assert type(incident) == AutomonFirewallRuleIncident
    return incident


def firewall_check_incident(
        responses: list[IncidentSearchResponse],
        security_rule: PanoramaSecurityRule
) -> tuple[list[AutomonFirewallRuleIncident], list[AutomonFirewallRuleIncident]]:
    debug(f'[firewall_check_incident] :: {responses=}', level=4)

    incidents_not_exists = []
    incidents_exists = []

    _INCIDENT_FOUND = False

    incidents = []
    for response in responses:
        incidents.extend(response.automon_incidents())

    for incident in incidents:
        if incident.name == security_rule.automon_incident_name():
            _INCIDENT_FOUND = True

            incident = AutomonFirewallRuleIncident(incident).update_from_security_rule(security_rule)

            debug(f'[firewall_check_incident] :: security rule found :: {security_rule}', level=4)
            debug(f'[firewall_check_incident] :: incident exists :: {incident}', level=3)
            incidents_exists.append(incident)

    if not _INCIDENT_FOUND:
        incident_to_be_created = AutomonFirewallRuleIncident().update_from_security_rule(security_rule)
        if incident_to_be_created not in incidents_not_exists:
            debug(f'[firewall_check_incident] :: incident_to_be_created :: {incident_to_be_created}', level=3)
            incidents_not_exists.append(incident_to_be_created)

    debug(f'[firewall_check_incident] :: {len(incidents_exists)} Incidents exists', level=2)
    debug(f'[firewall_check_incident] :: {len(incidents_not_exists)} Incidents to be created', level=2)

    debug(f'[firewall_check_incident] :: done')
    return incidents_exists, incidents_not_exists


def firewall_get_security_rule_last_hit(
        incidents: list[AutomonFirewallRuleIncident],
        security_rule,
) -> tuple[list[AutomonFirewallRuleIncident], list[AutomonFirewallRuleIncident]]:
    panos_responses = []

    for incident in incidents:
        panos_response = executeCommand_panos_get_last_hit(security_rule)
        panos_responses.extend(panos_response)

        incident.customFields['automonsecurityrulehitcountrawjson'] = [x.to_dict() for x in panos_response]

        for hits in panos_response:
            hits = hits.automon_get_rule_hit_count()

            incident = update_incidents_with_last_hit(incident, hits)

    debug(f'[firewall_get_security_rule_last_hit] :: {incidents}', level=4)
    debug(f'[firewall_get_security_rule_last_hit] :: {len(incidents)} incidents updated', level=2)
    return incidents, panos_responses


def firewall_get_security_rule_incident(security_rule: PanoramaSecurityRule) -> list[IncidentSearchResponse]:
    assert security_rule

    incident_name = security_rule.automon_incident_name()
    incident_type = 'AUTOMON_FirewallRule'

    size = 9999
    command = 'getIncidents'
    command_args = {
        'query': f'name:"{incident_name}" type:{incident_type}',
        "size": size,
    }

    # command_args = {
    #     'name': incident_name,
    #     'type': incident_type,
    #     "size": size,
    # }

    print_command(command, command_args)

    getIncidents = executeCommand_getIncidents(command_args)

    debug(f'[firewall_get_security_rule_incident] :: done')
    return getIncidents


def ignored_firewall_device_groups_postrulebase(Panorama: dict) -> list:
    assert Panorama['DeviceGroupNames']

    device_groups = Panorama['DeviceGroupNames']
    assert type(device_groups) == list
    assert device_groups

    debug(f'[ignored_firewall_device_groups_postrulebase] :: {len(device_groups)} device_groups', level=2)
    debug(f'[ignored_firewall_device_groups_postrulebase] :: {device_groups}', level=3)

    DeviceGroupNamesPostrulebase = []

    for device_group in device_groups:

        if device_group in IGNORED_DEVICE_GROUPS_POST_RULEBASE:
            debug(f'[ignored_firewall_device_groups_postrulebase] :: {device_group=} :: SKIPPED', level=2)
            continue
        else:
            debug(f'[ignored_firewall_device_groups_postrulebase] :: {device_group=} :: OK', level=3)

        DeviceGroupNamesPostrulebase.append(device_group)

    debug(f'[ignored_firewall_device_groups_postrulebase] :: {len(DeviceGroupNamesPostrulebase)} DeviceGroupNames',
          level=2)
    debug(f'[ignored_firewall_device_groups_postrulebase] :: {DeviceGroupNamesPostrulebase=}', level=3)
    debug(f'[ignored_firewall_device_groups_postrulebase] :: done')
    return DeviceGroupNamesPostrulebase


def ignored_firewall_device_groups_prerulebase(Panorama: dict) -> list:
    assert Panorama['DeviceGroupNames']

    device_groups = Panorama['DeviceGroupNames']
    assert type(device_groups) == list
    assert device_groups

    debug(f'[ignored_firewall_device_groups_prerulebase] :: {len(device_groups)} device_groups', level=2)
    debug(f'[ignored_firewall_device_groups_prerulebase] :: {device_groups}', level=3)

    DeviceGroupNamesPrerulebase = []

    for device_group in device_groups:

        if device_group in IGNORED_DEVICE_GROUPS:
            debug(f'[ignored_firewall_device_groups_prerulebase] :: {device_group=} :: SKIPPED', level=2)
            continue
        else:
            debug(f'[ignored_firewall_device_groups_prerulebase] :: {device_group=} :: OK', level=3)

        DeviceGroupNamesPrerulebase.append(device_group)

    debug(f'[ignored_firewall_device_groups_prerulebase] :: {len(DeviceGroupNamesPrerulebase)} DeviceGroupNames',
          level=2)
    debug(f'[ignored_firewall_device_groups_prerulebase] :: {DeviceGroupNamesPrerulebase=}', level=3)
    debug(f'[ignored_firewall_device_groups_prerulebase] :: done')
    return DeviceGroupNamesPrerulebase


def count_security_rules(Panorama: dict) -> list:
    assert Panorama
    assert type(Panorama) == dict

    security_rules = Panorama['SecurityRule']

    if type(security_rules) is not list:
        security_rules = [security_rules]

    assert type(security_rules) == list

    CountSecurityRules = []

    try:
        for security_rule in security_rules:
            assert type(security_rule) == dict
            security_rule = PanoramaSecurityRule().update(security_rule)

            if security_rule not in CountSecurityRules:
                CountSecurityRules.append(security_rule)
                debug(f'[count_rules] :: {security_rule=}', level=4)

    except Exception as error:
        import traceback
        raise Exception(f'[count_rules] :: ERROR :: {error=}')

    debug(f'[count_rules] :: {len(CountSecurityRules)} security rules', level=2)
    debug(f'[count_rules] :: done')

    CountSecurityRules = [f'{x}' for x in CountSecurityRules]

    return CountSecurityRules
