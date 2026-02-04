

## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from local_dev.demistoWrapper import *
    from local_dev.demistoWrapper import __line__
    # from local_dev.common.debugging import *
    # from local_dev.common import *
    from typing import Optional
except:
    pass

register_module_line('IllumioCore', 'start', __line__())
CONSTANT_PACK_VERSION = '1.0.27'
demisto.debug('pack id = Illumio, pack version = 1.0.27')

"""Implementation file for IllumioCore Integration."""
import json
from datetime import datetime
from enum import Enum
from typing import Any

import urllib3
from illumio import IllumioException, PolicyComputeEngine, Workload, convert_draft_href_to_active
from illumio.explorer import TrafficQuery
from illumio.policyobjects import ServiceBinding, ServicePort, VirtualService
from illumio.rules import EnforcementBoundary, Rule
from illumio.util import EnforcementMode, IllumioEncoder, Reference, convert_protocol

urllib3.disable_warnings()
""" CONSTANTS """

SUPPORTED_ENFORCEMENT_MODES = ["visibility_only", "full", "idle", "selective"]
SUPPORTED_VISIBILITY_LEVEL = [
    "flow_full_detail",
    "flow_summary",
    "flow_drops",
    "flow_off",
    "enhanced_data_collection",
]
TRAFFIC_MIN_PORT = 1
MIN_PORT = 0
MAX_PORT = 65535
HR_DATE_FORMAT = "%d %b %Y, %I:%M %p"
VALID_POLICY_DECISIONS = ["potentially_blocked", "blocked", "unknown", "allowed"]
VALID_PROTOCOLS = ["tcp", "udp"]
EXISTING_VIRTUAL_SERVICE = "Name must be unique"
EXISTING_ENFORCEMENT_BOUNDARY = "Rule name already in use"
EXISTING_RULESET = "Rule set name is already in use"
EXISTING_OBJECT = "One or more specified objects either don't exist, or do not have a draft version."


class Protocol(Enum):
    """Enum for protocols."""

    TCP = 6
    UDP = 17


""" EXCEPTION CLASS """


class InvalidValueError(Exception):
    """Custom exception class for invalid values."""

    def __init__(self, arg_name="", arg_value="", arg_list=[], message=""):
        if not message:
            message = f"{arg_value} is an invalid value for {arg_name}. Possible values are: {arg_list}"
        super().__init__(message)


""" HELPER FUNCTIONS """


def validate_required_parameters(**kwargs) -> None:
    """Raise an error for a required parameter.

    Enter your required parameters as keyword arguments to check
    whether they hold a value or not.

    Args:
        **kwargs: keyword arguments to check the required values for.

    Returns:
        Error if the value of the parameter is "", [], (), {}, None.
    """
    for key, value in kwargs.items():
        if not value and value is not False:
            raise ValueError(f"{key} is a required parameter. Please provide correct value.")


def trim_spaces_from_args(args: dict) -> dict:
    """Trim spaces from values of the args dict.

    Args:
        args: Dict to trim spaces from.

    Returns: Arguments after trim spaces.
    """
    for key, val in args.items():
        if isinstance(val, str):
            args[key] = val.strip()

    return args


def extract_values_from_dictionary(response: list) -> list:
    """Extract values from dictionary.
    Args:
        response: Response from the SDK.

    Returns:
        value of the key.
    """
    values = []
    for item in response:
        for key, value in item.items():
            if key == "actors":
                return [value]
        values.append(value.get("href"))
    return values


def generate_change_description_for_object_provision(hrefs: list[str]) -> str:
    """
    Generate a unique message for object provision command's change description argument.

    Args:
        hrefs: List of HREFs to be provisioned.

    Returns:
        str: A string with the current time in UTC.
    """
    return "XSOAR - {}\nProvisioning following objects:\n{}".format(datetime.utcnow().isoformat(), ", ".join(hrefs))


def validate_traffic_analysis_arguments(port: Optional[int], policy_decisions: list, protocol: str) -> None:
    """Validate arguments for traffic-analysis command.

    Args:
        port: Port number.
        policy_decisions: Policy decision to include in the search result.
        protocol: Communication protocol.
    """
    if port < TRAFFIC_MIN_PORT or port > MAX_PORT:  # type: ignore
        raise InvalidValueError(message=f"{port} invalid value for port. Value must be in 1 to 65535.")

    for decision in policy_decisions:
        if decision not in VALID_POLICY_DECISIONS:
            raise InvalidValueError("policy_decisions", decision, VALID_POLICY_DECISIONS)

    if protocol not in VALID_PROTOCOLS:
        raise InvalidValueError("protocol", protocol, VALID_PROTOCOLS)


def validate_virtual_service_arguments(port: Optional[int], protocol: str) -> None:
    """Validate arguments for virtual-service-create command.

    Args:
        port: Port number.
        protocol: Protocol name.
    """
    if port != -1 and (port > MAX_PORT or port < MIN_PORT):  # type: ignore
        raise InvalidValueError(message=f"{port} is an invalid value for port. Value must be in 0 to 65535 or -1.")

    if protocol not in VALID_PROTOCOLS:
        raise InvalidValueError("protocol", protocol, VALID_PROTOCOLS)


def validate_workloads_list_arguments(
        max_results: Optional[int],
        online: Optional[str],
        managed: Optional[str],
        enforcement_mode: Optional[str],
        visibility_level: Optional[str],
) -> None:
    """Validate arguments for workloads-list command.

    Args:
        max_results: Number of maximum results returned.
        online: Workload is online or not (yes, no).
        managed: Workload is managed or not (yes, no).
        enforcement_mode: Workload enforcement mode.
        visibility_level: Workload visibility level.
    """
    if isinstance(max_results, int) and (max_results < 1):  # type: ignore
        raise InvalidValueError(
            message=f"{max_results} is an invalid value for max_results. Max results must be positive integer."
        )

    if online:
        argToBoolean(online)

    if managed:
        argToBoolean(managed)

    if enforcement_mode and (enforcement_mode not in SUPPORTED_ENFORCEMENT_MODES):
        raise InvalidValueError("enforcement_mode", enforcement_mode, SUPPORTED_ENFORCEMENT_MODES)

    if visibility_level and (visibility_level not in SUPPORTED_VISIBILITY_LEVEL):
        raise InvalidValueError("visibility_level", visibility_level, SUPPORTED_VISIBILITY_LEVEL)


def validate_enforcement_boundary_create_arguments(port: Optional[int], protocol: str) -> None:
    """Validate arguments for enforcement-boundary-create command.

    Args:
        port: Port number.
        protocol: Protocol name.
    """
    if port > MAX_PORT or port < MIN_PORT:  # type: ignore
        raise InvalidValueError(message=f"{port} is an invalid value for port. Value must be in 0 to 65535.")

    if protocol not in VALID_PROTOCOLS:
        raise InvalidValueError("protocol", protocol, VALID_PROTOCOLS)


def validate_ip_lists_get_arguments(max_results: Optional[int], ip_address: Optional[str]) -> None:
    """Validate arguments for ip-lists-get command.

    Args:
        max_results: Number of maximum results returned.
        ip_address: IP address of ip lists to be returned.
    """
    if isinstance(max_results, int) and (max_results < 1):  # type: ignore
        raise InvalidValueError(
            message=f"{max_results} is an invalid value for max_results. Max results must be positive integer."
        )

    if ip_address and not is_ipv6_valid(ip_address):
        try:
            socket.inet_aton(ip_address)  # type: ignore
        except:  # noqa
            raise InvalidValueError(message=f"{ip_address} is an invalid value for ip_address.")


def prepare_traffic_analysis_output(response: list) -> str:
    """Prepare human-readable output for traffic-analysis-command.

    Args:
        response: Response from the SDK.

    Returns:
        markdown string to be displayed in the war room.
    """
    hr_output = []

    for traffic in response:
        hr_output.append(
            {
                "Source IP": traffic.get("src", {}).get("ip"),
                "Destination IP": traffic.get("dst", {}).get("ip"),
                "Destination Workload Hostname": traffic.get("dst", {}).get("workload", {}).get("hostname"),
                "Service Port": traffic.get("service", {}).get("port"),
                "Service Protocol": Protocol(traffic.get("service").get("proto")).name,
                "Policy Decision": traffic.get("policy_decision"),
                "State": traffic.get("state"),
                "Flow Direction": traffic.get("flow_direction"),
                "First Detected": arg_to_datetime(traffic["timestamp_range"]["first_detected"]).strftime(
                    # type: ignore
                    HR_DATE_FORMAT
                )
                if traffic.get("timestamp_range", {}).get("first_detected")
                else None,
                "Last Detected": arg_to_datetime(traffic["timestamp_range"]["last_detected"]).strftime(  # type: ignore
                    HR_DATE_FORMAT
                )
                if traffic.get("timestamp_range", {}).get("last_detected")
                else None,
            }
        )

    headers = list(hr_output[0].keys()) if hr_output else []

    return tableToMarkdown("Traffic Analysis:", hr_output, headers=headers, removeNull=True)


def prepare_virtual_service_output(response: dict) -> str:
    """Prepare human-readable output for virtual-service-create command.

    Args:
        response: Result returned after creating Virtual Service.

    Returns:
        markdown string to be displayed in the war room.
    """
    hr_output = []
    for service_port in response.get("service_ports", []):
        hr_output.append(
            {
                "Virtual Service HREF": response.get("href"),
                "Created At": arg_to_datetime(response["created_at"]).strftime(  # type: ignore
                    HR_DATE_FORMAT
                )
                if response.get("created_at")
                else None,
                "Updated At": arg_to_datetime(response["updated_at"]).strftime(  # type: ignore
                    HR_DATE_FORMAT
                )
                if response.get("updated_at")
                else None,
                "Name": response.get("name"),
                "Description": response.get("description"),
                "Service Port": service_port.get("port", "all ports have been selected"),
                "Service Protocol": Protocol(service_port.get("proto")).name,
            }
        )

    headers = list(hr_output[0].keys()) if hr_output else []

    title = "Virtual Service:\n#### Successfully created virtual service: {}\n".format(response.get("href"))
    return tableToMarkdown(title, hr_output, headers=headers, removeNull=True)


def prepare_service_binding_output(response: dict) -> str:
    """Prepare human-readable output for service-binding-create command.

    Args:
        response: result returned after create service binding.

    Returns:
        markdown string to be displayed in the war room.
    """
    hr_outputs = []

    if response.get("errors") and not response.get("service_bindings"):
        title = "Service Binding:\n#### Workloads are already bounded to the virtual service."
    else:
        for result in response.get("service_bindings", []):
            hr_outputs.append({"Service Binding HREF": result["href"], "Status": "created"})
        title = "Service Binding:\n#### Workloads have been bounded to the virtual service successfully."

    headers = list(hr_outputs[0].keys()) if hr_outputs else []
    return tableToMarkdown(title, hr_outputs, headers=headers, removeNull=True)


def prepare_object_provision_output(response: dict[str, Any]) -> str:
    """
    Prepare human-readable output for objects-provision command.

    Args:
        response: Response received from the SDK.

    Returns:
        str: Human-readable markdown string.
    """
    created_at = response.get("created_at")
    if created_at:
        created_at = arg_to_datetime(created_at).strftime(HR_DATE_FORMAT)  # type: ignore

    hr_output = {
        "Provision Object URI": response.get("href"),
        "Commit Message": response.get("commit_message"),
        "Created At": created_at,
    }

    return tableToMarkdown(
        "Provision Objects:",
        hr_output,
        headers=["Provision Object URI", "Commit Message", "Created At"],
        metadata="Provision is completed for {}".format(response.get("href")),
        removeNull=True,
    )


def prepare_workload_get_output(response: dict) -> str:
    """Prepare human-readable output for workload-get command.

    Args:
        response: Response from the SDK.

    Returns:
        markdown string to be displayed in the war room.
    """
    title = "Workload Details:"

    hr_outputs = {
        "Workload HREF": response.get("href"),
        "Name": response.get("name"),
        "Description": response.get("description"),
        "Created At": arg_to_datetime(response["created_at"]).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("created_at")
        else None,
        "Updated At": arg_to_datetime(response["updated_at"]).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("updated_at")
        else None,
        "Hostname": response.get("hostname"),
    }

    headers = list(hr_outputs.keys())
    return tableToMarkdown(title, hr_outputs, headers=headers, removeNull=True)


def prepare_workloads_list_output(response: list) -> str:
    """Prepare human-readable output for workloads-list command.

    Args:
        response: list of workloads in dict format.

    Returns:
        markdown string to be displayed in the war room.
    """
    hr_outputs = []
    for workload in response:
        hr_outputs.append(
            {
                "Workload HREF": workload.get("href"),
                "Name": workload.get("name"),
                "Hostname": workload.get("hostname"),
                "Description": workload.get("description"),
                "Enforcement Mode": workload.get("enforcement_mode"),
                "Visibility Level": workload.get("visibility_level"),
                "IP Address": workload.get("public_ip"),
                "Created At": arg_to_datetime(workload["created_at"]).strftime(  # type: ignore
                    HR_DATE_FORMAT
                )
                if workload.get("created_at")
                else None,
                "Updated At": arg_to_datetime(workload["updated_at"]).strftime(  # type: ignore
                    HR_DATE_FORMAT
                )
                if workload.get("updated_at")
                else None,
            }
        )

    headers = list(hr_outputs[0].keys()) if hr_outputs else []
    return tableToMarkdown("Workloads:\n", hr_outputs, headers=headers, removeNull=True)


def prepare_enforcement_boundary_create_output(response: dict) -> str:
    """Prepare human-readable output for enforcement-boundary-create command.

    Args:
        response: Result returned after creating enforcement boundary.

    Returns:
        markdown string to be displayed in the war room.
    """
    ingress_services = []

    for ingress_service in response.get("ingress_services", []):
        ingress_service_formatted = ""

        if "href" in ingress_service:
            ingress_service_formatted = ingress_service.get("href")
        elif "port" in ingress_service and "proto" in ingress_service:
            ingress_service_formatted = "{}-{}".format(ingress_service.get("port"),
                                                       Protocol(ingress_service.get("proto")).name)

        if ingress_service_formatted:
            ingress_services.append(ingress_service_formatted)

    hr_outputs = {
        "Enforcement Boundary HREF": response.get("href"),
        "Name": response.get("name"),
        "Created At": arg_to_datetime(response["created_at"]).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("created_at")
        else None,
        "Updated At": arg_to_datetime(response["updated_at"]).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("updated_at")
        else None,
        "Ingress Services": ingress_services,
    }

    headers = list(hr_outputs.keys())
    return tableToMarkdown("Enforcement Boundary:\n", hr_outputs, headers=headers, removeNull=True)


def prepare_update_enforcement_mode_output(response: list):
    """Prepare Human Readable output for enforcement-mode-update command.

    Args:
        response: Response from the SDK.

    Returns:
        markdown string to be displayed in the war room.
    """
    hr_outputs = []
    headers = ["Workload HREF", "Status"]
    successful_update_count = 0
    failed_update_count = 0

    for resp in response:
        if resp.get("errors"):
            failed_update_count += 1
            hr_outputs.append({"Workload HREF": resp.get("href"), "Status": "Failed"})
        else:
            successful_update_count += 1
            hr_outputs.append({"Workload HREF": resp.get("href"), "Status": "Updated"})

    title = (
        "Workload Enforcement Update:\n#### Successfully updated enforcement "
        f"mode for {successful_update_count} workloads, {failed_update_count} workloads failed to update"
    )

    return tableToMarkdown(title, hr_outputs, headers=headers, removeNull=True)


def ip_list_human_readable(response: dict) -> dict:
    """Prepare dictionary for ip list.

    Args:
        response: Response from the SDK.

    Returns:
        Dictionary for ip list.
    """
    hr_output = {
        "IP List HREF": response.get("href", ""),
        "Name": response.get("name", ""),
        "Created At": arg_to_datetime(response.get("created_at")).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("created_at")
        else None,
        "Updated At": arg_to_datetime(response.get("updated_at")).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("updated_at")
        else None,
        "IP Ranges": ", ".join(
            [
                ip_range.get("from_ip") + (" - " + ip_range["to_ip"] if ip_range.get("to_ip") else "")
                for ip_range in response.get("ip_ranges", [])
            ]
        ),
        "FQDNs": ", ".join([fqdn_rec["fqdn"] for fqdn_rec in response.get("fqdns", [])]),
    }

    return hr_output


def prepare_ip_list_get_output(response: dict) -> str:
    """Prepare human-readable output for ip-list-get command.

    Args:
        response: Response from the SDK.

    Returns:
        markdown string to be displayed in the war room.
    """
    hr_output = ip_list_human_readable(response)

    headers = list(hr_output.keys())
    return tableToMarkdown("IP List Details:", hr_output, headers=headers, removeNull=True)


def prepare_ip_lists_get_output(response: list) -> str:
    """Prepare human-readable output for ip-lists-get command.

    Args:
        response: list of IllumioObject in dict format.

    Returns:
        markdown string to be displayed in the war room.
    """
    hr_outputs = []
    for ip_list in response:
        hr_outputs.append(ip_list_human_readable(ip_list))

    headers = list(hr_outputs[0].keys()) if hr_outputs else []
    return tableToMarkdown("IP Lists:", hr_outputs, headers=headers, removeNull=True)


def prepare_ruleset_create_output(response: dict, name: Optional[Any]):
    """Prepare Human Readable output for create ruleset command.

    Args:
        response: Response from the SDK.
        name: Name of the ruleset.

    Returns:
        markdown string to be displayed in the war room.
    """
    hr_output = {
        "Ruleset HREF": response.get("href"),
        "Name": name,
        "Created At": arg_to_datetime(response["created_at"]).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("created_at")
        else None,
        "Updated At": arg_to_datetime(response["updated_at"]).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("updated_at")
        else None,
        "Enabled": response.get("enabled"),
        "Rules": response.get("rules"),
        "Caps": response.get("caps"),
    }

    headers = list(hr_output.keys())
    title = f"Ruleset {name} has been created successfully."

    return tableToMarkdown(title, hr_output, headers=headers, removeNull=True)


def prepare_rule_create_output(response: dict) -> str:
    """Prepare Human Readable output for create rule command.

    Args:
        response: Response from the SDK.

    Returns:
        markdown string to be displayed in the war room.
    """
    hr_output = {
        "Rule HREF": response.get("href"),
        "Description": response.get("description"),
        "Created At": arg_to_datetime(response["created_at"]).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("created_at")
        else None,
        "Updated At": arg_to_datetime(response["updated_at"]).strftime(  # type: ignore
            HR_DATE_FORMAT
        )
        if response.get("updated_at")
        else None,
        "Enabled": response.get("enabled"),
        "Network Type": response.get("network_type"),
        "Ingress Services": ", ".join([resp.get("href") for resp in response.get("ingress_services", [])]),
        "Providers": extract_values_from_dictionary(response.get("providers")),  # type: ignore
        "Consumers": extract_values_from_dictionary(response.get("consumers")),  # type: ignore
        "Resolve Providers As": response["resolve_labels_as"]["providers"],
        "Resolve Consumers As": response["resolve_labels_as"]["consumers"],
    }

    title = "Rule {} has been created successfully.".format(response.get("href"))
    headers = list(hr_output.keys())

    return tableToMarkdown(title, hr_output, headers=headers, removeNull=True)


def debug(log: str = '\n', level: int = 1, json_output: bool = False):
    if json_output:
        import json
        log = json.dumps(log)
    else:
        log = str(log)

    if 'DEBUG' not in globals():
        DEBUG = 1

    if level <= DEBUG:
        print(log)


class Dict:

    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.to_dict()}"

    def __eq__(self, other):
        if self.__dict__ == other.__dict__:
            return True
        return False

    def _flatten(self) -> dict:
        flatten = {}

        for key, value in self.__dict__.items():

            if key == 'CustomFields':
                continue

            if type(value) == dict:
                flatten.update(self._flatten_dict(value))
            elif type(value) == list:
                flatten.update(self._flatten_list(key, value))
            else:
                flatten[key] = value

        return flatten

    def _flatten_dict(self, value: dict) -> dict:
        flatten = {}

        if type(value) == dict:
            for item in value.items():
                key, value = item

                if type(value) == list:
                    flatten.update(self._flatten_list(key, value))

                elif type(value) == dict:
                    flatten.update(self._flatten_dict(value))

                else:
                    flatten[key] = value

        return flatten

    def _flatten_list(self, key: str, value: list) -> dict:

        flatten = {}

        if type(value) == list:
            for value_ in value:
                if type(value_) == dict:
                    flatten.update(self._flatten_dict(value_))
                elif type(value_) == list:
                    flatten.update(self._flatten_list(key, value_))
                else:
                    flatten[key] = value

        return flatten

    def _update(self, update: dict | str | object):

        if isinstance(update, str):
            return self._update_json(update)

        if hasattr(update, '__dict__'):
            update = update.__dict__

        return self._update_dict(update)

    def _update_dict(self, update: dict):
        self.__dict__.update(update)
        return self

    def _update_json(self, update: str):
        import json
        update = json.loads(update)
        return self._update_dict(update)

    def update(self, update: dict | str):
        return self._update(update)

    def to_dict(self):
        if self.to_json():
            return self.__dict__
        raise Exception(f"[Dict] :: ERROR :: can't serialized :: {self.__dict__}")

    def _to_json(self, indent: int = None):
        import json
        try:
            return json.dumps(self.__dict__, indent=indent)
        except Exception as error:
            raise Exception(f'ERROR :: {error=} :: {self.__dict__}')

    def to_json(self, indent: int = None):
        return self._to_json(indent)


class AutomonDemisto(object):
    _args: dict
    _command: str
    _params: dict
    _credentials: dict

    def __init__(self):

        self._args: dict = demisto.args()
        self._command: str = demisto.command()
        self._params: dict = demisto.params()
        self._credentials: dict = {}

    def args(self, arg: str):
        return self._args.get(arg)

    @property
    def command(self):
        return self._command

    def getCredential(self, credential: str) -> str | int | bool | None:
        """this only works if the credentials are retrieved and then stored into the integration

        yeah I know, it makes no sense. you can't pull directly from the xsoar Credentials
        """

        debug(f"{demisto.credentials(credential)=}")

        self._credentials[credential] = demisto.credentials(credential)
        username: str = self._credentials[credential].get('user')
        password: str = self._credentials[credential].get('password')
        workgroup: str = self._credentials[credential].get('workgroup')
        certificate: str = self._credentials[credential].get('certificate')

        if username:
            if 'false' in username.lower():
                return False
            if 'true' in username.lower():
                return True
            try:
                return int(username)
            except:
                return username

        if password:
            return password

        if workgroup:
            return workgroup

        if certificate:
            return certificate

    def params(self, param: str = None):
        if param:
            value = self._params.get(param)

            if not value:
                return value

            value = str(self._params.get(param))
            value = value.strip()

            if 'true' in value.lower():
                return True

            if 'false' in value.lower():
                return False

            try:
                return int(value)
            except:
                pass

            return value

        return self._params


class AutomonDemistoFetchTimer(object):

    def __init__(self, fetch_start: int = 1):
        from datetime import datetime, timedelta

        self.last_run = demisto.getLastRun()
        self.time_now = datetime.now()
        self.time_now_timestamp = int(self.time_now.timestamp())

        self.start_time = self.last_run.get('start_time')

        self.fetch_start = fetch_start

        try:
            assert type(self.start_time) == int, f'ERROR :: {self.start_time=}'
        except:
            self.start_time = self.time_now_timestamp

        if self.last_run and self.start_time:
            self.start_time = self.start_time + 1
        else:
            self.start_time = round(
                (self.time_now - timedelta(days=self.fetch_start)).timestamp() * 1000
            )

    def created_at_epoch_sec(self, seconds: int):
        import time
        seconds = int(seconds)
        try:
            # divide by 1000 to turn milliseconds to seconds
            # or microseconds to milliseconds ???
            created_at_epoch_sec = int(seconds / 1000)
        except:
            created_at_epoch_sec = int(time.time())
        return created_at_epoch_sec

    def created_at_date(self, seconds: int) -> datetime:
        from datetime import datetime, timezone

        created_at_epoch_sec = self.created_at_epoch_sec(seconds)
        return datetime.fromtimestamp(round(created_at_epoch_sec), timezone.utc)


class AutomonIndicatorVerdict(Enum):
    Malicious = 'Malicious'
    Suspicious = 'Suspicious'
    Benign = 'Benign'
    Unknown = 'Unknown'


class AutomonIndicatorType(Enum):
    IP = 'IP'
    IPv6 = 'IPv6'
    Domain = 'Domain'
    URL = 'URL'
    File = 'File'
    File_MD5 = 'File MD5'
    File_SHA1 = 'File SHA1'
    File_SHA256 = 'File SHA256'
    Email = 'Email'
    Host = 'Host'
    CIDR = 'CIDR'
    Registry_Key = 'Registry Key'
    Malware = 'Malware'
    Threat_Actor = 'Threat Actor'
    Campaign = 'Campaign'
    CVE = 'CVE'


class AutomonIndicatorSeverity(Enum):
    """
    Severity Level 	JSON/Integer Value
    Critical	    4
    High	        3
    Medium	        2
    Low	            1
    Informational	0.5
    Unknown	        0
    """
    Critical = 'Critical'
    High = 'High'
    Medium = 'Medium'
    Low = 'Low'
    Informational = 'Informational'
    Unknown = 'Unknown'


class AutomonIndicatorExpiration(object):
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self):
        self.date = None

    def now(self):
        from datetime import datetime, timezone
        self.date = datetime.now(timezone.utc)
        return self

    def years(self, years: int = 1):
        days = years * 12 * 31
        self.days(days)
        return self

    def months(self, months: int = 1):
        days = months * 31
        self.days(days)
        return self

    def days(self, days: int = 1):
        from datetime import timedelta

        current_datetime = self.now().date

        days_to_add = timedelta(days=days)
        future_datetime = current_datetime + days_to_add
        self.date = future_datetime
        return self

    def hours(self, hours: int = 1):
        minutes = hours * 60
        self.minutes(minutes)
        return self

    def minutes(self, minutes: int | float = 1):
        from datetime import timedelta

        current_time = self.now().date
        time_delta = timedelta(minutes=minutes)
        future_time = current_time + time_delta
        self.date = future_time
        return self

    def seconds(self, seconds: int = 1):
        minutes = seconds / 60
        self.minutes(minutes)
        return self

    def to_string(self):
        return self.date.strftime(self.datetime_format)


class AutomonIncidentOccurred(AutomonIndicatorExpiration):

    def __init__(self):
        super().__init__()


class AutomonIndicatorStatus(Enum):
    Active = 'Active'
    Expired = 'Expired'


class AutomonIndicator(Dict):

    def __init__(self):
        super().__init__()

        self.value: str = ''
        self.type: str = ''
        self.description: str = ''
        self.tags: list[str] = []
        self.severity: str | AutomonIndicatorSeverity = AutomonIndicatorSeverity.Unknown
        self.expiration: str | AutomonIndicatorExpiration = ''
        self.rawJSON: dict = {}

    def set_value(self, value: str):
        self.value = value
        return self

    def set_type(self, type: str):
        self.type = type
        return self

    def set_description(self, description: str = None):
        if description:
            self.description = description
        return self

    def set_tags(self, tags: list[str] = None):
        if tags:
            self.tags = tags
        return self

    def set_severity(self, severity: str | AutomonIndicatorSeverity = None):
        if severity:
            self.severity = severity
        return self

    def set_expiration(self, expiration: str | AutomonIndicatorExpiration = None):
        if expiration:
            self.expiration = expiration
        return self

    def update_rawJSON(self, update: dict):
        assert type(update) is dict, f"[ERROR] :: {update=}"
        self.rawJSON.update(update)
        return self


class AutomonIncident(Dict):

    def __init__(self):
        """

        "name": "Suspicious Activity Detected on Host X",
        "type": "Malware",
        "severity": 3,
        "occurred": "2025-11-05T10:30:00Z",
        "details": "A user reported a suspicious executable running on their machine.",
        "labels": [
        {
          "type": "source",
          "value": "EDR System"
        },
        {
          "type": "hostname",
          "value": "Host-X-Prod"
        }
        ],
        "createInvestigation": true,
        "owner": "Analyst Bob"

        """
        super().__init__()

        self.name: str = ''
        self.details: str = ''
        self.type: str = ''
        self.severity: AutomonIndicatorSeverity = AutomonIndicatorSeverity.Unknown
        self.occurred: AutomonIncidentOccurred | datetime = AutomonIncidentOccurred().now().to_string()
        self.owner: str = 'AutomonBot'
        self.createInvestigation: bool = True
        self.tags: list[str] = []

        self.rawJSON: str = ''


class IllumioConfig(Dict):

    def __init__(
            self,
            ILLUMIO_URL: str = None,
            ILLUMIO_PORT: int = None,
            ILLUMIO_API_USER: str = None,
            ILLUMIO_API_PASSWORD: str = None,
            ILLUIMO_ORG_ID: int = None,
            ILLUMIO_PROXY_HTTP: str = None,
            ILLUMIO_PROXY_HTTPS: str = None,
            ILLUMIO_CERT_VERIFY: bool = False,
    ):
        super().__init__()

        self.ILLUMIO_URL = ILLUMIO_URL or AutomonDemisto().params('ILLUMIO_URL')
        self.ILLUMIO_PORT = ILLUMIO_PORT or AutomonDemisto().params('ILLUMIO_PORT')

        self.ILLUMIO_API_USER = ILLUMIO_API_USER or AutomonDemisto().params('ILLUMIO_API_USER')
        self.ILLUMIO_API_PASSWORD = ILLUMIO_API_PASSWORD or AutomonDemisto().params('ILLUMIO_API_PASSWORD')

        self.ILLUIMO_ORG_ID = ILLUIMO_ORG_ID or AutomonDemisto().params('ILLUIMO_ORG_ID')

        self.ILLUMIO_PROXY_HTTP = ILLUMIO_PROXY_HTTP or AutomonDemisto().params('ILLUMIO_PROXY_HTTP')
        self.ILLUMIO_PROXY_HTTPS = ILLUMIO_PROXY_HTTPS or AutomonDemisto().params('ILLUMIO_PROXY_HTTPS')

        self.ILLUMIO_CERT_VERIFY = ILLUMIO_CERT_VERIFY or AutomonDemisto().params('ILLUMIO_CERT_VERIFY')

        if not self.ILLUMIO_URL or \
                not self.ILLUMIO_PORT or \
                not self.ILLUMIO_API_USER or \
                not self.ILLUMIO_API_PASSWORD or \
                not self.ILLUIMO_ORG_ID:
            raise Exception(f"[IllumioConfig] :: ERROR :: {self}")


class IllumioClient(object):

    def __init__(self, config: IllumioConfig = None):
        self.config = config or IllumioConfig()

    @property
    def client(self, **kwargs):
        client = PolicyComputeEngine(
            url=self.config.ILLUMIO_URL,
            port=self.config.ILLUMIO_PORT,
            org_id=self.config.ILLUIMO_ORG_ID,
            **kwargs
        )
        client.set_proxies(
            http_proxy=self.config.ILLUMIO_PROXY_HTTP,
            https_proxy=self.config.ILLUMIO_PROXY_HTTPS
        )
        client.set_credentials(
            username=self.config.ILLUMIO_API_USER,
            password=self.config.ILLUMIO_API_PASSWORD
        )
        return client

    def rule_create_command(self, args: dict[str, Any]) -> CommandResults:
        """Create and assign rules to a particular ruleset.

        Args:
            args: Arguments obtained from demisto.args()

        Returns:
            CommandResults: CommandResults object
        """
        ruleset_href = args["ruleset_href"]
        providers = args.get("providers")
        consumers = args.get("consumers")
        ingress_services = args.get("ingress_services")
        resolve_providers_as = args.get("resolve_providers_as", "workloads")
        resolve_consumers_as = args.get("resolve_consumers_as", "workloads")

        validate_required_parameters(ruleset_href=ruleset_href, providers=providers, consumers=consumers)
        providers = argToList(providers)
        consumers = argToList(consumers)
        ingress_services = argToList(ingress_services)
        resolve_providers_as = argToList(resolve_providers_as)
        resolve_consumers_as = argToList(resolve_consumers_as)

        # Building params to check whether rule is present in particular ruleset or not
        params = {
            "ingress_services": sorted(ingress_services),
            "providers": sorted(providers),
            "consumers": sorted(consumers),
            "resolve_providers_as": sorted(resolve_providers_as),
            "resolve_consumers_as": sorted(resolve_consumers_as),
        }

        ruleset = client.rule_sets.get_by_reference(ruleset_href)  # type: ignore[call-overload]
        ruleset_json = ruleset.to_json()
        for rules in ruleset_json.get("rules", []):
            existing_rule = {
                "ingress_services": sorted([href.get("href") for href in rules.get("ingress_services", {})]),
                "providers": sorted(extract_values_from_dictionary(rules.get("providers"))),
                "consumers": sorted(extract_values_from_dictionary(rules.get("consumers"))),
                "resolve_providers_as": sorted(rules.get("resolve_labels_as", {}).get("providers")),
                "resolve_consumers_as": sorted(rules.get("resolve_labels_as", {}).get("consumers")),
            }
            if params == existing_rule:
                demisto.debug(f"Found existing Rule bounded to the Ruleset: {ruleset_href}.")
                rule_href = rules.get("href")
                response = self.client.rules.get_by_reference(rule_href)
                break
        else:
            rule = Rule.build(
                ingress_services=ingress_services,
                consumers=consumers,
                providers=providers,
                resolve_consumers_as=resolve_consumers_as,
                resolve_providers_as=resolve_providers_as,
            )
            response = self.client.rules.create(rule, parent=ruleset_href)

        response = response.to_json()
        readable_output = prepare_rule_create_output(response)  # type: ignore[arg-type]

        return CommandResults(
            outputs_prefix="Illumio.Rule",
            outputs_key_field="href",
            outputs=remove_empty_elements(response),
            readable_output=readable_output,
            raw_response=response,
        )

    def ruleset_create_command(self, args: dict[str, Any]) -> CommandResults:
        """Create a ruleset with unique name.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        name = args.get("name")
        validate_required_parameters(name=name)
        try:
            response = self.client.rule_sets.create(body={"name": name, "scopes": [[]]})  # type: ignore[call-overload]
            json_response = response.to_json()
        except Exception as e:
            if EXISTING_RULESET in str(e):
                try:
                    rule_sets = self.client.rule_sets.get(params={"name": name})  # type: ignore[call-overload]
                    demisto.debug("Ruleset already exists.")
                    for rule_set in rule_sets:
                        if rule_set.name == name:
                            json_response = rule_set.to_json()
                            break
                except Exception as e:
                    raise Exception(f"Encountered error while creating Ruleset: {e}")
            else:
                raise Exception(f"Encountered error while creating Ruleset: {e}")  # type: ignore[misc]

        readable_output = prepare_ruleset_create_output(json_response, name)

        return CommandResults(
            outputs_prefix="Illumio.Ruleset",
            outputs_key_field="href",
            outputs=remove_empty_elements(json_response),
            readable_output=readable_output,
            raw_response=json_response,
        )

    def ip_lists_get_command(self, args: dict[str, Any]) -> CommandResults:
        """Retrieve the IP lists.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        description = args.get("description")
        fqdn = args.get("fqdn")
        ip_address = args.get("ip_address")
        max_results = arg_to_number(args.get("max_results", 500), arg_name="max_results")
        name = args.get("name")

        validate_ip_lists_get_arguments(max_results, ip_address)

        ip_lists = self.client.ip_lists.get(
            params={
                "description": description,
                "fqdn": fqdn,
                "ip_address": ip_address,
                "max_results": max_results,
                "name": name,
            }
        )  # type: ignore

        ip_lists_json = [ip_lists.to_json() for ip_lists in ip_lists]
        readable_output = prepare_ip_lists_get_output(ip_lists_json)

        return CommandResults(
            outputs_prefix="Illumio.IPLists",
            readable_output=readable_output,
            outputs_key_field="href",
            raw_response=ip_lists_json,
            outputs=[remove_empty_elements(ip_list) for ip_list in ip_lists_json],
        )

    def ip_list_get_command(self, args: dict[str, Any]) -> CommandResults:
        """Get the details of the IP List.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        href = args["href"]
        validate_required_parameters(href=href)

        response = self.client.ip_lists.get_by_reference(href)  # type: ignore[call-overload]
        results = json.loads(json.dumps(response, cls=IllumioEncoder))  # convert the ip_lists objects

        readable_output = prepare_ip_list_get_output(results)

        return CommandResults(
            outputs_prefix="Illumio.IPLists",
            outputs_key_field="href",
            outputs=remove_empty_elements(results),
            readable_output=readable_output,
            raw_response=results,
        )

    def update_enforcement_mode_command(self, args: dict[str, Any]) -> CommandResults:
        """Update enforcement mode for one or more workloads.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        enforcement_mode = args.get("enforcement_mode")
        workloads = argToList(args.get("workloads"))

        validate_required_parameters(enforcement_mode=enforcement_mode, workloads=workloads)

        enforcement_mode = EnforcementMode(enforcement_mode.lower())  # type: ignore
        workload = [Workload(href=href, enforcement_mode=enforcement_mode) for href in workloads]  # type: ignore

        response = self.client.workloads.bulk_update(workload)  # type: ignore
        results = json.loads(json.dumps(response, cls=IllumioEncoder))

        context_data = []
        for result in results:
            if result.get("errors"):
                context_data.append({"href": result.get("href"), "status": "Failed"})
            else:
                context_data.append({"href": result.get("href"), "status": "Updated"})

        readable_output = prepare_update_enforcement_mode_output(results)

        return CommandResults(
            outputs_prefix="Illumio.UpdateStatuses",
            readable_output=readable_output,
            outputs_key_field="href",
            outputs=remove_empty_elements(context_data),
            raw_response=results,
        )

    def enforcement_boundary_create_command(self, args: dict[str, Any]) -> CommandResults:
        """Create an enforcement boundary.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        name = args.get("name")
        port = args.get("port")
        protocol = args.get("protocol", "tcp").lower()
        providers = args.get("providers")
        consumers = args.get("consumers")

        validate_required_parameters(name=name, port=port, providers=providers, consumers=consumers)
        providers = argToList(providers)
        consumers = argToList(consumers)
        port = arg_to_number(port, arg_name="port")
        validate_enforcement_boundary_create_arguments(port, protocol)
        proto = convert_protocol(protocol)

        enforcement_boundary_rule = EnforcementBoundary.build(
            name=name,
            consumers=consumers,
            providers=providers,
            ingress_services=[{"port": port, "proto": proto}],
        )
        enforcement_boundary_json = {}
        try:
            enforcement_boundary = self.client.enforcement_boundaries.create(
                enforcement_boundary_rule)  # type: ignore[call-overload]
            enforcement_boundary_json = enforcement_boundary.to_json()
        except Exception as e:
            if EXISTING_ENFORCEMENT_BOUNDARY in str(e):
                try:
                    enforcement_boundaries = self.client.enforcement_boundaries.get(
                        params={"name": name})  # type: ignore[call-overload]
                    demisto.debug("Enforcement boundary already exists.")
                    for enforcement_boundary in enforcement_boundaries:
                        if enforcement_boundary.name == name:
                            enforcement_boundary_json = enforcement_boundary.to_json()
                            break
                except Exception as e:
                    raise Exception(f"Encountered error while retrieving enforcement boundary: {e}")
            else:
                raise Exception(f"Encountered error while creating enforcement boundary: {e}")  # type: ignore[misc]

        readable_output = prepare_enforcement_boundary_create_output(enforcement_boundary_json)

        return CommandResults(
            outputs_prefix="Illumio.EnforcementBoundary",
            readable_output=readable_output,
            outputs_key_field="href",
            raw_response=enforcement_boundary_json,
            outputs=remove_empty_elements(enforcement_boundary_json),
        )

    def workloads_list_command(self, args: dict[str, Any]) -> CommandResults:
        """Retrieve the workloads list.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        max_results = arg_to_number(args.get("max_results", 500), arg_name="max_results")
        name = args.get("name")
        hostname = args.get("hostname")
        ip_address = args.get("ip_address")
        online = args.get("online")
        managed = args.get("managed")
        labels = args.get("labels")
        enforcement_mode = args.get("enforcement_mode")
        visibility_level = args.get("visibility_level")

        validate_workloads_list_arguments(max_results, online, managed, enforcement_mode, visibility_level)

        if labels:
            labels = json.dumps([[x] for x in argToList(labels)])

        params = {
            "max_results": max_results,
            "name": name,
            "hostname": hostname,
            "ip_address": ip_address,
            "online": online,
            "managed": managed,
            "labels": labels,
            "enforcement_mode": enforcement_mode,
            "visibility_level": visibility_level,
        }
        workloads_list = self.client.workloads.get(params=params)  # type: ignore

        workloads_list_json = [workload.to_json() for workload in workloads_list]
        readable_output = prepare_workloads_list_output(workloads_list_json)

        return CommandResults(
            outputs_prefix="Illumio.Workloads",
            readable_output=readable_output,
            outputs_key_field="href",
            raw_response=workloads_list_json,
            outputs=remove_empty_elements(workloads_list_json),  # type: ignore
        )

    def object_provision_command(self, args: dict[str, Any]) -> CommandResults:
        """
        Command function for illumio-objects-provision command.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            Standard command results.
        """
        security_policy_objects = args.get("security_policy_objects", "")
        validate_required_parameters(security_policy_objects=security_policy_objects)
        security_policy_objects = argToList(security_policy_objects)
        change_description = generate_change_description_for_object_provision(hrefs=security_policy_objects)
        response_dict = {}
        try:
            response_object = self.client.provision_policy_changes(change_description=change_description,
                                                                   hrefs=security_policy_objects)
            response_dict = response_object.to_json()
            hr_output = prepare_object_provision_output(response_dict)

            # Converting draft HREFs to active
            provisioned_hrefs = [convert_draft_href_to_active(href) for href in security_policy_objects]

            response_dict["provisioned_hrefs"] = provisioned_hrefs
        except Exception as e:
            if EXISTING_OBJECT not in str(e):
                raise Exception(f"Encountered error while provisioning security policy object: {e}")
            else:
                hr_output = "### Security policy object(s) already provisioned: {}.".format(
                    ", ".join(security_policy_objects))

        return CommandResults(
            outputs_prefix="Illumio.PolicyState",
            outputs_key_field="href",
            outputs=remove_empty_elements(response_dict),
            readable_output=hr_output,
            raw_response=response_dict,
        )

    def workload_get_command(self, args: dict[str, Any]) -> CommandResults:
        """Retrieve a workload.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        href = args.get("href")
        validate_required_parameters(href=href)

        response = self.client.workloads.get_by_reference(href)  # type: ignore
        results = json.loads(json.dumps(response, cls=IllumioEncoder))

        readable_output = prepare_workload_get_output(results)

        return CommandResults(
            outputs_prefix="Illumio.Workloads",
            readable_output=readable_output,
            outputs_key_field="href",
            outputs=remove_empty_elements(results),
            raw_response=results,
        )

    def service_binding_create_command(self, args: dict[str, Any]) -> CommandResults:
        """Create a service binding.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        workloads = argToList(args["workloads"])
        virtual_service = args["virtual_service"]

        validate_required_parameters(workloads=workloads, virtual_service=virtual_service)

        virtual_service = convert_draft_href_to_active(virtual_service)
        try:
            self.client.virtual_services.get_by_reference(virtual_service)
        except IllumioException as e:
            raise InvalidValueError(message=f"no active record for virtual service with HREF {virtual_service}") from e

        service_bindings = [
            ServiceBinding(virtual_service=Reference(href=virtual_service), workload=Reference(href=href)) for href in
            workloads
        ]

        response = self.client.service_bindings.create(service_bindings)  # type: ignore[call-overload]
        results = json.loads(json.dumps(response, cls=IllumioEncoder))
        context_data = {"hrefs": [service.get("href", "") for service in results.get("service_bindings", [])]}
        readable_output = prepare_service_binding_output(results)

        return CommandResults(
            outputs_prefix="Illumio.ServiceBinding",
            readable_output=readable_output,
            outputs_key_field="href",
            outputs=remove_empty_elements(context_data),
            raw_response=results,
        )

    def virtual_service_create_command(self, args: dict[str, Any]) -> CommandResults:
        """Create a virtual service.

        Args:
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        protocol = args.get("protocol", "tcp").lower()
        name = args["name"]
        port: int = arg_to_number(args["port"], arg_name="port")  # type: ignore[assignment]

        validate_required_parameters(name=name, port=port)

        validate_virtual_service_arguments(port, protocol)
        proto = convert_protocol(protocol)

        service = VirtualService(name=name, service_ports=[ServicePort(port=port, proto=proto)])
        try:
            virtual_service = self.client.virtual_services.create(service)  # type: ignore[call-overload]
            virtual_service_json = virtual_service.to_json()
        except Exception as e:
            if EXISTING_VIRTUAL_SERVICE in str(e):
                try:
                    virtual_services = self.client.virtual_services.get(
                        params={"name": name})  # type: ignore[call-overload]
                    demisto.debug("Virtual service already exists.")
                    for virtual_service in virtual_services:
                        if virtual_service.name == name:
                            virtual_service_json = virtual_service.to_json()
                            break
                except Exception as e:
                    raise Exception(f"Encountered error while retrieving virtual service: {e}")
            else:
                raise Exception(f"Encountered error while creating virtual service: {e}")  # type: ignore[misc]

        readable_output = prepare_virtual_service_output(virtual_service_json)

        return CommandResults(
            outputs_prefix="Illumio.VirtualService",
            readable_output=readable_output,
            outputs_key_field="href",
            raw_response=virtual_service_json,
            outputs=remove_empty_elements(virtual_service_json),
        )

    def traffic_analysis_command(self, args: dict[str, Any]) -> CommandResults:
        """Retrieve the traffic for a particular port and protocol.

        Args:
            client: PolicyComputeEngine to use.
            args: arguments obtained from demisto.args()

        Returns:
            CommandResult object
        """
        port = arg_to_number(args.get("port"))
        protocol = args.get("protocol", "tcp").lower()
        start_time = arg_to_datetime(args.get("start_time", "1 week ago")).isoformat()  # type: ignore
        end_time = arg_to_datetime(args.get("end_time", "now")).isoformat()  # type: ignore
        policy_decisions = argToList(args.get("policy_decisions", "potentially_blocked,unknown"))

        validate_required_parameters(port=port)
        validate_traffic_analysis_arguments(port, policy_decisions, protocol)  # type: ignore

        query_name = f"XSOAR - Traffic analysis for port {port}: {datetime.now().isoformat()}"

        proto = convert_protocol(protocol)
        service = ServicePort(port, proto=proto)  # type: ignore
        traffic_query = TrafficQuery.build(
            start_date=start_time,
            end_date=end_time,
            policy_decisions=policy_decisions,
            include_services=[service],
        )

        response = self.client.get_traffic_flows_async(query_name=query_name, traffic_query=traffic_query)
        json_response = [resp.to_json() for resp in response]

        readable_output = prepare_traffic_analysis_output(json_response)

        return CommandResults(
            outputs_prefix="Illumio.TrafficFlows",
            outputs_key_field="href",
            outputs=remove_empty_elements(json_response),  # type: ignore
            readable_output=readable_output,
            raw_response=json_response,
        )

    def command_test_module(self, verify: bool = None) -> str:
        """Tests API connectivity and authentication.

        Returning 'ok' indicates that the integration works like it is supposed to.
        Connection to the service is successful.

        Returns: 'ok' if test passed, anything else will fail the test.
        """

        response = self.client.check_connection(verify=verify)
        if response:
            return "ok"
        raise Exception(f"[IllumioClient] :: command_test_module :: ERROR :: {self.client.__dict__=} :: {self.config=}")

    def fetch_incidents(self):
        import time

        create_incidents = []

        fetch_timer = AutomonDemistoFetchTimer(fetch_start=1)
        start_time = fetch_timer.start_time

        incidents = self.query_incidents()

        for incident in incidents:
            incident_type = incident.get('type')

            creation_time = int(incident.get('CreationTime'))
            created_at_date = fetch_timer.created_at_date(creation_time)

            xsoar_incident = AutomonIncident()
            xsoar_incident.name = f'ILLUMIO :: {incident_type}'
            xsoar_incident.rawJSON = incident
            xsoar_incident.occurred = created_at_date

            if creation_time > start_time:
                start_time = creation_time

            create_incidents.append(xsoar_incident)

        create_incidents.reverse()
        demisto.setLastRun({'start_time': start_time})
        demisto.incidents(create_incidents)

        return create_incidents

    def fetch_indicators(self):
        create_indicators = []

        indicators = self.query_indicators()

        for indicator in indicators:
            indicator_to_create = AutomonIndicator(
            ).set_value(
                indicator.get('value')
            ).set_type(
                indicator.get('type')
            ).set_description(
                indicator.get('description')
            ).set_severity(
                AutomonIndicatorSeverity.Informational
            ).set_expiration(
                AutomonIndicatorExpiration().days(7).to_string()
            ).update_rawJSON(
                indicator
            ).to_dict()

            create_indicators.append(indicator_to_create)
            demisto.createIndicators(indicator_to_create)

        return create_indicators

    def query_incidents(self) -> list:
        return []

    def query_indicators(self) -> list:
        return []


def main():
    client = IllumioClient()

    command = AutomonDemisto().command
    params = AutomonDemisto().params()

    if command == "test-module":
        return_results(client.command_test_module(verify=client.config.ILLUMIO_CERT_VERIFY))
    if command == 'fetch-incidents':
        debug(f'[main] :: fetch-incidents :: {command=}')
        client.fetch_incidents()
    if command == 'fetch-indicators':
        debug(f'[main] :: fetch-incidents :: {command=}')
        client.fetch_indicators()
    else:
        illumio_commands = {
            "illumio-traffic-analysis": client.traffic_analysis_command,
            "illumio-virtual-service-create": client.virtual_service_create_command,
            "illumio-service-binding-create": client.service_binding_create_command,
            "illumio-object-provision": client.object_provision_command,
            "illumio-workload-get": client.workload_get_command,
            "illumio-workloads-list": client.workloads_list_command,
            "illumio-enforcement-boundary-create": client.enforcement_boundary_create_command,
            "illumio-enforcement-mode-update": client.update_enforcement_mode_command,
            "illumio-ip-list-get": client.ip_list_get_command,
            "illumio-ip-lists-get": client.ip_lists_get_command,
            "illumio-ruleset-create": client.ruleset_create_command,
            "illumio-rule-create": client.rule_create_command,
            "test-module": client.command_test_module,
        }
        if command in illumio_commands:
            args = demisto.args()
            remove_nulls_from_dictionary(trim_spaces_from_args(args))
            return_results(illumio_commands[command](args))
        else:
            raise NotImplementedError(f"Command {command} is not implemented")


if __name__ in ("__main__", "__builtin__", "builtins"):  # pragma: no cover
    main()

register_module_line('IllumioCore', 'end', __line__())
