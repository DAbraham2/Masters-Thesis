from transport import BaseTransport
from interface.ble import MinimalBleDevice, BleUtils, BleState
from plugins.soc import OtUpCli, ZigbeeBleDmpCli


class DmpApplication(MinimalBleDevice, BleUtils):
    def __init__(self, transport: BaseTransport):
        self._transport = transport
        self._thread = OtUpCli()
        self._ble = ZigbeeBleDmpCli()
        self._ble_state = BleState.STANDBY

    def _init_handlers(self):
        hs = self._thread.get_handlers()
        for k, v in hs:
            self._transport.register_handler(v, k)

    def start_scanning(self) -> bool:
        try:
            self._ble.start_scan(self._transport, discovery_mode=0x2)
            self._ble_state = BleState.STANDBY
            return True
        except Exception:
            return False

    def stop_scanning(self) -> bool:
        try:
            self._ble.stop_scan(self._transport)
            self._ble_state = BleState.STANDBY
            return True
        except Exception:
            return False

    def start_advertising(self) -> bool:
        try:
            self._ble.enter_connectable(
                self._transport,
                adv_handle=0x0,
                discovery_mode=0x2,
                connectable_mode=0x2,
            )
            self._ble_state = BleState.ADVERTISING
            return True
        except Exception:
            return False

    def stop_advertising(self) -> bool:
        try:
            self._ble.stop_advertise(self._transport, handle=0x0)
            self._ble_state = BleState.STANDBY
            return True
        except Exception:
            return False

    def get_state(self) -> BleState:
        return self._ble_state

    def get_address(self) -> bytes:
        return b'B00B5'
