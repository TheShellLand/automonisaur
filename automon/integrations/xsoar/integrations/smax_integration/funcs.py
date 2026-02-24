## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from automon.integrations.xsoar.local_testing import *
    from automon.integrations.xsoar.demistoWrapper import *
    # from local_dev.common import *
except:
    pass


def executeCommand_smax_query_request(command_args) -> list[SmaxQueryTicketResponse]:
    import json

    command = 'smax-query-request'

    print_command(command, command_args)

    try:
        response = demisto.executeCommand('smax-query-request', command_args)
    except Exception as error:
        raise Exception(f"ERROR :: {error=} :: {command=} :: {command_args=}")

    debug(f'[smax_get_ticket] :: response :: {json.dumps(response)}', level=4)
    response = [SmaxQueryTicketResponse(x) for x in response]
    debug(f'[smax_get_ticket] :: response :: {response}', level=2)
    return response


def executeCommand_smax_query_person(command_args) -> list[SmaxQueryPersonResponse]:
    import json

    print_command('smax_query_person', command_args)

    response = demisto.executeCommand('smax_query_person', command_args)

    debug(f'[smax_get_person] :: response :: {json.dumps(response)}', level=4)
    response = [SmaxQueryPersonResponse(x) for x in response]
    debug(f'[smax_get_person] :: response :: {response}', level=2)
    return response


def update_incident_with_smax_person(
        incident: AutomonFirewallRuleIncident
) -> tuple[Incident, list[dict]]:
    automon_custom_smax_id_fields = incident.automon_custom_smax_id_fields()

    smax_query_person_responses = []

    for _key in automon_custom_smax_id_fields:
        ids = automon_custom_smax_id_fields[_key]

        try:
            ids = [int(x) for x in ids]
        except:
            continue

        for id_ in ids:
            command = 'smax_query_person'
            command_args = dict(
                id=id_,
                using='smax',
            )
            print_command(command, command_args)

            smax_query_person_response = executeCommand_smax_query_person(command_args)

            for response in smax_query_person_response:
                incident = smax_update_person(incident, response)

            smax_query_person_responses.extend(smax_query_person_response)

    debug(f'[smax_get_person] :: {incident=}', level=2)
    return incident, smax_query_person_responses


def update_incidents_with_smax_ticket(
        incident: AutomonFirewallRuleIncident,
        security_rule: PanoramaSecurityRule
) -> tuple[Incident, list[dict]]:
    assert type(incident) == AutomonFirewallRuleIncident, f'ERROR :: incident :: {incident}'

    smax_query_request_responses = []
    smax_ids = security_rule.automon_get_smax_from_description()

    for smax_id in smax_ids:

        command = 'smax-query-request'
        command_args = dict(
            id=int(smax_id),
            filter="RequestType = 'SupportRequest'",
            using='smax',
        )
        print_command(command, command_args)

        smax_query_request_response = executeCommand_smax_query_request(command_args)

        for response in smax_query_request_response:
            incident = smax_update_ticket(incident, response)

            smax_query_request_responses.append(response)

    debug(f'[smax_get_ticket] :: {len(smax_query_request_responses)} smax searches', level=3)
    return incident, smax_query_request_responses


def smax_update_ticket(
        incident: AutomonFirewallRuleIncident,
        response: SmaxQueryTicketResponse
) -> AutomonFirewallRuleIncident:
    incident.update_from_smax_ticket(response)

    for smax_entities in response.automon_smax_tickets():
        automon_ExpertAssignee = smax_entities.automon_ExpertAssignee
        automon_ManagerialContact_c = smax_entities.automon_ManagerialContact_c
        automon_TechnicalContact_c = smax_entities.automon_TechnicalContact_c
        automon_ArchitectName_c = smax_entities.automon_ArchitectName_c

        automonsmaxexpertassignee = incident.customFields['automonsmaxexpertassignee']
        automonsmaxmanagerialcontact = incident.customFields['automonsmaxmanagerialcontact']
        automonsmaxtechnicalcontact = incident.customFields['automonsmaxtechnicalcontact']
        automonsmaxarchitectname = incident.customFields['automonsmaxarchitectname']

        for item in automon_ExpertAssignee:
            if item not in automonsmaxexpertassignee:
                incident.customFields['automonsmaxexpertassignee'].append(item)

        for item in automon_ManagerialContact_c:
            if item not in automonsmaxmanagerialcontact:
                incident.customFields['automonsmaxmanagerialcontact'].append(item)

        for item in automon_TechnicalContact_c:
            if item not in automonsmaxtechnicalcontact:
                incident.customFields['automonsmaxtechnicalcontact'].append(item)

        for item in automon_ArchitectName_c:
            if item not in automonsmaxarchitectname:
                incident.customFields['automonsmaxarchitectname'].append(item)

    debug(f'[smax_get_ticket] :: {incident.to_json()}', level=2)
    debug(f'[smax_get_ticket] :: {incident}', level=2)
    return incident


def smax_update_person(
        incident: AutomonFirewallRuleIncident,
        smax_query_person_response: SmaxQueryPersonResponse
) -> AutomonFirewallRuleIncident:
    persons = smax_query_person_response.automon_smax_entities()

    for person in persons:
        incident.update_from_smax_person(person)

    debug(f'[smax_get_person] :: {incident.to_json()}', level=4)
    debug(f'[smax_get_person] :: {incident}', level=2)
    return incident


def smax_get_ticket(
        incidents,
        security_rule,
) -> tuple[list[AutomonFirewallRuleIncident], list[AutomonFirewallRuleIncident]]:
    debug(f'[smax_get_ticket] :: incidents :: {len(incidents)}', level=2)

    smax_query_response_list = []

    for incident in incidents:
        incident, _smax_query_response_list = update_incidents_with_smax_ticket(incident, security_rule)
        smax_query_response_list.extend(_smax_query_response_list)

    debug(f'[smax_get_ticket] :: {len(incidents)} Incidents updated', level=2)
    return incidents, smax_query_response_list


def smax_get_person(
        incidents
) -> tuple[list[AutomonFirewallRuleIncident], list[AutomonFirewallRuleIncident]]:
    responses = []

    for incident in incidents:
        incident, responses = update_incident_with_smax_person(incident)

        responses.extend(responses)

    debug(f'[smax_get_person] :: Incidents updated :: {len(incidents)}', level=2)
    return incidents, responses
