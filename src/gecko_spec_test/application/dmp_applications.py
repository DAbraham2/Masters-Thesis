from transport import BaseTransport
from interface.ble import MinimalBleDevice, BleUtils, BleState


class DmpApplication(MinimalBleDevice, BleUtils):
    def __init__(self, transport: BaseTransport):
        self._transport = transport

    def start_scanning(self) -> bool:
        raise NotImplementedError()

    def stop_scanning(self) -> bool:
        raise NotImplementedError()

    def start_advertising(self) -> bool:
        raise NotImplementedError()

    def stop_advertising(self) -> bool:
        raise NotImplementedError()

    def get_state(self) -> BleState:
        raise NotImplementedError()

    def get_address(self) -> bytes:
        raise NotImplementedError()
