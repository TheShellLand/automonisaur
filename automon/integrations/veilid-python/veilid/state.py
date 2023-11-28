from enum import StrEnum
from typing import Optional, Self

from .config import VeilidConfig
from .types import (
    ByteCount,
    RouteId,
    Timestamp,
    TimestampDuration,
    TypedKey,
    ValueData,
    ValueSubkey,
    VeilidLogLevel,
    OperationId,
    urlsafe_b64decode_no_pad,
)


class AttachmentState(StrEnum):
    DETACHED = "Detached"
    ATTACHING = "Attaching"
    ATTACHED_WEAK = "AttachedWeak"
    ATTACHED_GOOD = "AttachedGood"
    ATTACHED_STRONG = "AttachedStrong"
    FULLY_ATTACHED = "FullyAttached"
    OVER_ATTACHED = "OverAttached"
    DETACHING = "Detaching"


class VeilidStateAttachment:
    state: AttachmentState
    public_internet_ready: bool
    local_network_ready: bool

    def __init__(
        self,
        state: AttachmentState,
        public_internet_ready: bool,
        local_network_ready: bool,
    ):
        self.state = state
        self.public_internet_ready = public_internet_ready
        self.local_network_ready = local_network_ready

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            AttachmentState(j["state"]),
            j["public_internet_ready"],
            j["local_network_ready"],
        )


class RPCStats:
    messages_sent: int
    messages_rcvd: int
    questions_in_flight: int
    last_question_ts: Optional[Timestamp]
    last_seen_ts: Optional[Timestamp]
    first_consecutive_seen_ts: Optional[Timestamp]
    recent_lost_answers: int
    failed_to_send: int

    def __init__(
        self,
        messages_sent: int,
        messages_rcvd: int,
        questions_in_flight: int,
        last_question_ts: Optional[Timestamp],
        last_seen_ts: Optional[Timestamp],
        first_consecutive_seen_ts: Optional[Timestamp],
        recent_lost_answers: int,
        failed_to_send: int,
    ):
        self.messages_sent = messages_sent
        self.messages_rcvd = messages_rcvd
        self.questions_in_flight = questions_in_flight
        self.last_question_ts = last_question_ts
        self.last_seen_ts = last_seen_ts
        self.first_consecutive_seen_ts = first_consecutive_seen_ts
        self.recent_lost_answers = recent_lost_answers
        self.failed_to_send = failed_to_send

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            j["messages_sent"],
            j["messages_rcvd"],
            j["questions_in_flight"],
            None if j["last_question_ts"] is None else Timestamp(j["last_question_ts"]),
            None if j["last_seen_ts"] is None else Timestamp(j["last_seen_ts"]),
            None
            if j["first_consecutive_seen_ts"] is None
            else Timestamp(j["first_consecutive_seen_ts"]),
            j["recent_lost_answers"],
            j["failed_to_send"],
        )


class LatencyStats:
    fastest: TimestampDuration
    average: TimestampDuration
    slowest: TimestampDuration

    def __init__(
        self,
        fastest: TimestampDuration,
        average: TimestampDuration,
        slowest: TimestampDuration,
    ):
        self.fastest = fastest
        self.average = average
        self.slowest = slowest

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            TimestampDuration(j["fastest"]),
            TimestampDuration(j["average"]),
            TimestampDuration(j["slowest"]),
        )


class TransferStats:
    total: ByteCount
    maximum: ByteCount
    average: ByteCount
    minimum: ByteCount

    def __init__(
        self,
        total: ByteCount,
        maximum: ByteCount,
        average: ByteCount,
        minimum: ByteCount,
    ):
        self.total = total
        self.maximum = maximum
        self.average = average
        self.minimum = minimum

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            ByteCount(j["total"]),
            ByteCount(j["maximum"]),
            ByteCount(j["average"]),
            ByteCount(j["minimum"]),
        )


class TransferStatsDownUp:
    down: TransferStats
    up: TransferStats

    def __init__(self, down: TransferStats, up: TransferStats):
        self.down = down
        self.up = up

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(TransferStats.from_json(j["down"]), TransferStats.from_json(j["up"]))


class PeerStats:
    time_added: Timestamp
    rpc_stats: RPCStats
    latency: Optional[LatencyStats]
    transfer: TransferStatsDownUp

    def __init__(
        self,
        time_added: Timestamp,
        rpc_stats: RPCStats,
        latency: Optional[LatencyStats],
        transfer: TransferStatsDownUp,
    ):
        self.time_added = time_added
        self.rpc_stats = rpc_stats
        self.latency = latency
        self.transfer = transfer

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            j["time_added"],
            RPCStats.from_json(j["rpc_stats"]),
            None if j["latency"] is None else LatencyStats.from_json(j["latency"]),
            TransferStatsDownUp.from_json(j["transfer"]),
        )


class PeerTableData:
    node_ids: list[str]
    peer_address: str
    peer_stats: PeerStats

    def __init__(self, node_ids: list[str], peer_address: str, peer_stats: PeerStats):
        self.node_ids = node_ids
        self.peer_address = peer_address
        self.peer_stats = peer_stats

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(j["node_ids"], j["peer_address"], PeerStats.from_json(j["peer_stats"]))


class VeilidStateNetwork:
    started: bool
    bps_down: ByteCount
    bps_up: ByteCount
    peers: list[PeerTableData]

    def __init__(
        self,
        started: bool,
        bps_down: ByteCount,
        bps_up: ByteCount,
        peers: list[PeerTableData],
    ):
        self.started = started
        self.bps_down = bps_down
        self.bps_up = bps_up
        self.peers = peers

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            j["started"],
            ByteCount(j["bps_down"]),
            ByteCount(j["bps_up"]),
            [PeerTableData.from_json(peer) for peer in j["peers"]],
        )


class VeilidStateConfig:
    config: VeilidConfig

    def __init__(self, config: VeilidConfig):
        self.config = config

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(VeilidConfig.from_json(j["config"]))


class VeilidState:
    attachment: VeilidStateAttachment
    network: VeilidStateNetwork
    config: VeilidStateConfig

    def __init__(
        self,
        attachment: VeilidStateAttachment,
        network: VeilidStateNetwork,
        config: VeilidStateConfig,
    ):
        self.attachment = attachment
        self.network = network
        self.config = config

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            VeilidStateAttachment.from_json(j["attachment"]),
            VeilidStateNetwork.from_json(j["network"]),
            VeilidStateConfig.from_json(j["config"]),
        )


class VeilidLog:
    log_level: VeilidLogLevel
    message: str
    backtrace: Optional[str]

    def __init__(self, log_level: VeilidLogLevel, message: str, backtrace: Optional[str]):
        self.log_level = log_level
        self.message = message
        self.backtrace = backtrace

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(VeilidLogLevel(j["log_level"]), j["message"], j["backtrace"])


class VeilidAppMessage:
    sender: Optional[TypedKey]
    message: bytes

    def __init__(self, sender: Optional[TypedKey], message: bytes):
        self.sender = sender
        self.message = message

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            None if j["sender"] is None else TypedKey(j["sender"]),
            urlsafe_b64decode_no_pad(j["message"]),
        )


class VeilidAppCall:
    sender: Optional[TypedKey]
    message: bytes
    call_id: OperationId

    def __init__(self, sender: Optional[TypedKey], message: bytes, call_id: OperationId):
        self.sender = sender
        self.message = message
        self.call_id = call_id

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            None if j["sender"] is None else TypedKey(j["sender"]),
            urlsafe_b64decode_no_pad(j["message"]),
            OperationId(j["call_id"]),
        )


class VeilidRouteChange:
    dead_routes: list[RouteId]
    dead_remote_routes: list[RouteId]

    def __init__(self, dead_routes: list[RouteId], dead_remote_routes: list[RouteId]):
        self.dead_routes = dead_routes
        self.dead_remote_routes = dead_remote_routes

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            [RouteId(route) for route in j["dead_routes"]],
            [RouteId(route) for route in j["dead_remote_routes"]],
        )


class VeilidValueChange:
    key: TypedKey
    subkeys: list[ValueSubkey]
    count: int
    value: ValueData

    def __init__(self, key: TypedKey, subkeys: list[ValueSubkey], count: int, value: ValueData):
        self.key = key
        self.subkeys = subkeys
        self.count = count
        self.value = value

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        return cls(
            TypedKey(j["key"]),
            [ValueSubkey(key) for key in j["subkeys"]],
            j["count"],
            ValueData.from_json(j["value"]),
        )


class VeilidUpdateKind(StrEnum):
    LOG = "Log"
    APP_MESSAGE = "AppMessage"
    APP_CALL = "AppCall"
    ATTACHMENT = "Attachment"
    NETWORK = "Network"
    CONFIG = "Config"
    ROUTE_CHANGE = "RouteChange"
    VALUE_CHANGE = "ValueChange"
    SHUTDOWN = "Shutdown"


VeilidUpdateDetailType = Optional[
    VeilidLog
    | VeilidAppMessage
    | VeilidAppCall
    | VeilidStateAttachment
    | VeilidStateNetwork
    | VeilidStateConfig
    | VeilidRouteChange
    | VeilidValueChange
]


class VeilidUpdate:
    kind: VeilidUpdateKind
    detail: VeilidUpdateDetailType

    def __init__(
        self,
        kind: VeilidUpdateKind,
        detail: VeilidUpdateDetailType,
    ):
        self.kind = kind
        self.detail = detail

    @classmethod
    def from_json(cls, j: dict) -> Self:
        """JSON object hook"""
        kind = VeilidUpdateKind(j["kind"])
        detail: VeilidUpdateDetailType = None
        match kind:
            case VeilidUpdateKind.LOG:
                detail = VeilidLog.from_json(j)
            case VeilidUpdateKind.APP_MESSAGE:
                detail = VeilidAppMessage.from_json(j)
            case VeilidUpdateKind.APP_CALL:
                detail = VeilidAppCall.from_json(j)
            case VeilidUpdateKind.ATTACHMENT:
                detail = VeilidStateAttachment.from_json(j)
            case VeilidUpdateKind.NETWORK:
                detail = VeilidStateNetwork.from_json(j)
            case VeilidUpdateKind.CONFIG:
                detail = VeilidStateConfig.from_json(j)
            case VeilidUpdateKind.ROUTE_CHANGE:
                detail = VeilidRouteChange.from_json(j)
            case VeilidUpdateKind.VALUE_CHANGE:
                detail = VeilidValueChange.from_json(j)
            case VeilidUpdateKind.SHUTDOWN:
                detail = None
            case _:
                raise ValueError("Unknown VeilidUpdateKind")
        return cls(kind, detail)
