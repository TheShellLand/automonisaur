from dataclasses import dataclass, fields
from enum import StrEnum
from typing import Optional, Self

from .types import TypedKey, TypedSecret, Capability


class VeilidConfigLogLevel(StrEnum):
    OFF = "Off"
    ERROR = "Error"
    WARN = "Warn"
    INFO = "Info"
    DEBUG = "Debug"
    TRACE = "Trace"


@dataclass
class ConfigBase:
    @classmethod
    def from_json(cls, json_data: dict) -> Self:
        """Return an instance of this type from the input data."""
        args = {}
        for field in fields(cls):
            key = field.name
            value = json_data[key]
            try:
                # See if this field's type knows how to load itself from JSON input.
                loader = field.type.from_json
            except AttributeError:
                # No, it doesn't. Use the raw value.
                args[key] = value
            else:
                # Yes, it does. Use the loading function's output.
                args[key] = loader(value)

        return cls(**args)

    def to_json(self) -> dict:
        return self.__dict__


@dataclass
class VeilidConfigCapabilities(ConfigBase):
    disable: list[Capability]


@dataclass
class VeilidConfigProtectedStore(ConfigBase):
    allow_insecure_fallback: bool
    always_use_insecure_storage: bool
    directory: str
    delete: bool
    device_encryption_key_password: str
    new_device_encryption_key_password: Optional[str]


@dataclass
class VeilidConfigTableStore(ConfigBase):
    directory: str
    delete: bool


@dataclass
class VeilidConfigBlockStore(ConfigBase):
    directory: str
    delete: bool


@dataclass
class VeilidConfigRoutingTable(ConfigBase):
    node_id: list[TypedKey]
    node_id_secret: list[TypedSecret]
    bootstrap: list[str]
    limit_over_attached: int
    limit_fully_attached: int
    limit_attached_strong: int
    limit_attached_good: int
    limit_attached_weak: int


@dataclass
class VeilidConfigRPC(ConfigBase):
    concurrency: int
    queue_size: int
    max_timestamp_behind_ms: Optional[int]
    max_timestamp_ahead_ms: Optional[int]
    timeout_ms: int
    max_route_hop_count: int
    default_route_hop_count: int


@dataclass
class VeilidConfigDHT(ConfigBase):
    max_find_node_count: int
    resolve_node_timeout_ms: int
    resolve_node_count: int
    resolve_node_fanout: int
    get_value_timeout_ms: int
    get_value_count: int
    get_value_fanout: int
    set_value_timeout_ms: int
    set_value_count: int
    set_value_fanout: int
    min_peer_count: int
    min_peer_refresh_time_ms: int
    validate_dial_info_receipt_time_ms: int
    local_subkey_cache_size: int
    local_max_subkey_cache_memory_mb: int
    remote_subkey_cache_size: int
    remote_max_records: int
    remote_max_subkey_cache_memory_mb: int
    remote_max_storage_space_mb: int


@dataclass
class VeilidConfigTLS(ConfigBase):
    certificate_path: str
    private_key_path: str
    connection_initial_timeout_ms: int


@dataclass
class VeilidConfigHTTPS(ConfigBase):
    enabled: bool
    listen_address: str
    path: str
    url: Optional[str]


@dataclass
class VeilidConfigHTTP(ConfigBase):
    enabled: bool
    listen_address: str
    path: str
    url: Optional[str]


@dataclass
class VeilidConfigApplication(ConfigBase):
    https: VeilidConfigHTTPS
    http: VeilidConfigHTTP


@dataclass
class VeilidConfigUDP(ConfigBase):
    enabled: bool
    socket_pool_size: int
    listen_address: str
    public_address: Optional[str]


@dataclass
class VeilidConfigTCP(ConfigBase):
    connect: bool
    listen: bool
    max_connections: int
    listen_address: str
    public_address: Optional[str]


@dataclass
class VeilidConfigWS(ConfigBase):
    connect: bool
    listen: bool
    max_connections: int
    listen_address: str
    path: str
    url: Optional[str]


@dataclass
class VeilidConfigWSS(ConfigBase):
    connect: bool
    listen: bool
    max_connections: int
    listen_address: str
    path: str
    url: Optional[str]


@dataclass
class VeilidConfigProtocol(ConfigBase):
    udp: VeilidConfigUDP
    tcp: VeilidConfigTCP
    ws: VeilidConfigWS
    wss: VeilidConfigWSS


@dataclass
class VeilidConfigNetwork(ConfigBase):
    connection_initial_timeout_ms: int
    connection_inactivity_timeout_ms: int
    max_connections_per_ip4: int
    max_connections_per_ip6_prefix: int
    max_connections_per_ip6_prefix_size: int
    max_connection_frequency_per_min: int
    client_allowlist_timeout_ms: int
    reverse_connection_receipt_time_ms: int
    hole_punch_receipt_time_ms: int
    network_key_password: Optional[str]
    routing_table: VeilidConfigRoutingTable
    rpc: VeilidConfigRPC
    dht: VeilidConfigDHT
    upnp: bool
    detect_address_changes: bool
    restricted_nat_retries: int
    tls: VeilidConfigTLS
    application: VeilidConfigApplication
    protocol: VeilidConfigProtocol


@dataclass
class VeilidConfig(ConfigBase):
    program_name: str
    namespace: str
    capabilities: VeilidConfigCapabilities
    protected_store: VeilidConfigProtectedStore
    table_store: VeilidConfigTableStore
    block_store: VeilidConfigBlockStore
    network: VeilidConfigNetwork
