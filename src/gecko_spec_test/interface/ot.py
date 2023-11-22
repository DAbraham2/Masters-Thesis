from dataclasses import dataclass
from typing import Protocol, Optional


@dataclass
class ThreadNetworkData:
    pan_id: bytes = bytes(2)
    """16-bit unsigned integer that must be different from 0xFFFF"""

    network_key: bytes = bytes(16)
    """16 bytes crypto-random number"""

    network_name: str = ''
    """A human-readable name of the network in 16 byte length"""

    channel: int = -1
    """15.4 channel number"""


class ThreadUtils(Protocol):
    def get_dataset(self) -> ThreadNetworkData:
        ...

    def get_ip_address(self) -> str:
        ...

    def factory_reset(self) -> None:
        ...

    def get_thread_state(self) -> str:
        ...


class ThreadDevice(Protocol):
    def join_thread_network(self, channel: int, pan_id: bytes):
        ...

    def join_network_with_nwk_key(self, network_key: bytes):
        ...


class ThreadCoordinator(Protocol):
    def create_network(
        self, *, channel: Optional[int] = None, pan_id: Optional[bytes] = None
    ):
        ...
