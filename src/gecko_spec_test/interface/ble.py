from enum import auto, Flag
from typing import Protocol


class BleState(Flag):
    STANDBY = auto()
    ADVERTISING = auto()
    SCANNING = auto()
    INITIATING = auto()
    CONNECTION = auto()
    SYNCHRONIZATION = auto()
    ISO_BROADCAST = auto()


class BleUtils(Protocol):
    def get_state(self) -> BleState:
        ...

    def get_address(self) -> bytes:
        ...


class MinimalBleDevice(Protocol):
    def start_scanning(self) -> bool:
        ...

    def stop_scanning(self) -> bool:
        ...

    def start_advertising(self) -> bool:
        ...

    def stop_advertising(self) -> bool:
        ...


class InitiatorBleDevice(Protocol):
    def init_connection(self, address: bytes) -> tuple[bool, int]:
        ...

    def disconnect(self, connection: int) -> bool:
        ...
