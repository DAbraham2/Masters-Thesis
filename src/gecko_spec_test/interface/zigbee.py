from typing import Protocol
from plugins.cli.zigbeee import ZigbeeStatus


class ZigbeeUtils(Protocol):
    def get_node_id(self) -> bytes:
        ...

    def get_zig_state(self) -> ZigbeeStatus:
        ...


class ZigbeeDevice(Protocol):
    def join_network(self, channel: int):
        ...

    def leave_network(self):
        ...


class ZigbeeCoordinator(Protocol):
    def create_network(self, channel: int, pan_id: bytes):
        ...


class ZigbeeThroughputable(Protocol):
    def start_throughput(self) -> bool:
        ...

    def wait_for_results(self) -> float:
        ...
