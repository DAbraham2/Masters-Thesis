from typing import Protocol


class ZigbeeUtils(Protocol):
    def get_node_id(self) -> bytes:
        ...


class ZigbeeDevice(Protocol):
    def join_network(self):
        ...

    def leave_network(self):
        ...


class ZigbeeCoordinator(Protocol):
    def create_network(self):
        ...


class ZigbeeThroughputable(Protocol):
    def start_throughput(self) -> bool:
        ...

    def wait_for_results(self) -> float:
        ...
