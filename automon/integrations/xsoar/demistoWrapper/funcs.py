## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from automon.integrations.xsoar.local_testing import *
    from automon.integrations.xsoar.demistoWrapper import *
    # from local_dev.common import *
except:
    pass

DEBUG = 3


def debug(log: str = '\n', level: int = 1, json_output: bool = False):
    if json_output:
        import json
        log = json.dumps(log)
    else:
        log = str(log)

    if level <= DEBUG:
        print(log)


def debug_error(log: str, level: int = 1):
    import traceback
    print(traceback.format_exc())
    if DEBUG <= level:
        print(f'{log}')


def print_command(command: str, command_args: dict):
    import json
    command_args_str = ' '.join([f'{k}={json.dumps(v)}' for k, v in command_args.items()])
    executeCommand = f'''!{command} {command_args_str}'''

    debug(f'[print_command] :: command_args :: {command_args}', level=2)
    debug(f'[print_command] :: executeCommand :: {executeCommand}', level=2)

    return executeCommand


def executeCommand_createNewIncident(command_args) -> list[IncidentCreateResponse]:
    import json

    print_command('createNewIncident', command_args)

    response = demisto.executeCommand('createNewIncident', command_args)

    debug(f'[xsoar_create_incident] :: {json.dumps(response)}', level=4)
    response = [IncidentCreateResponse(x) for x in response if x]
    debug(f'[xsoar_create_incident] :: {response=}', level=4)
    return response


def executeCommand_getIncidents(command_args) -> [IncidentSearchResponse]:
    import json

    print_command('getIncidents', command_args)

    response = demisto.executeCommand("getIncidents", command_args)

    assert type(response) == list
    debug(f'[firewall_get_security_rule_incident] :: response :: {json.dumps(response)}', level=3)

    response = [IncidentSearchResponse().update(x) for x in response]

    total = [x.Contents['total'] for x in response]
    debug(f'[firewall_get_security_rule_incident] :: response :: {response}', level=2)
    debug(f'[firewall_get_security_rule_incident] :: total :: {total}', level=2)
    return response


def executeCommand_setIncident(incident_to_update) -> list[IncidentUpdateResponse]:
    import json

    response = demisto.executeCommand('setIncident', incident_to_update)

    debug(f'[xsoar_update_incident] :: response :: {json.dumps(response)}', level=3)
    response = [IncidentUpdateResponse(x) for x in response if x]
    debug(f'[xsoar_update_incident] :: response :: {response}', level=3)
    return response


def xsoar_create_incident(
        incidents: list[AutomonFirewallRuleIncident]
) -> tuple[list[AutomonFirewallRuleIncident], list[IncidentCreateResponse]]:
    createNewIncident_responses = []
    for incident in incidents:
        command_args = incident.to_create_incident()

        createNewIncident_response = executeCommand_createNewIncident(command_args)
        createNewIncident_responses.extend(createNewIncident_response)

    debug(f'[xsoar_create_incident] :: {len(incidents)} incidents created', level=2)
    return incidents, createNewIncident_responses


def xsoar_update_incident(
        incidents: list[AutomonFirewallRuleIncident]
) -> tuple[list[AutomonFirewallRuleIncident], list[IncidentUpdateResponse]]:
    setIncident_responses = []

    for incident in incidents:
        incident_to_update = incident.to_update_incident()

        setIncident_response = executeCommand_setIncident(incident_to_update)

        setIncident_responses.extend(setIncident_response)

    debug(f'[xsoar_update_ticket] :: {len(incidents)} Incidents updated', level=2)
    return incidents, setIncident_responses


def xsoar_validation(
        incidents: list[AutomonFirewallRuleIncident]
) -> list[AutomonFirewallRuleIncident]:
    for incident in incidents:

        customFields = [
            'automonfirewallrulerawjson',
            'automonsecurityrulehitcountrawjson',
            'automonsmaxrawjson',
        ]

        for customField in customFields:
            if not incident.customFields[customField]:
                incident.tags.append('error')

    # if 'error' in incident.tags:
    #     raise Exception(f'{incident} :: {incident.to_json()}')

    return incidents
