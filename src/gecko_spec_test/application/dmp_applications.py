from transport import BaseTransport
from interface.ble import MinimalBleDevice, BleUtils, BleState
from interface.zigbee import ZigbeeDevice, ZigbeeThroughputable, ZigbeeUtils
from interface.ot import ThreadUtils, ThreadDevice, ThreadNetworkData
from plugins.soc import OtUpCli, ZigbeeBleDmpCli
from plugins.cli.zigbeee import ZigbeeCore, ZigbeeStatus
import plugins.cli.zigbeee as zig_cli


class DmpApplication(
    MinimalBleDevice,
    BleUtils,
    ZigbeeUtils,
    ZigbeeDevice,
    ZigbeeThroughputable,
    ThreadUtils,
    ThreadDevice,
):
    def __init__(self, transport: BaseTransport):
        self._transport = transport
        self._thread = OtUpCli()
        self._ble = ZigbeeBleDmpCli()
        self._ble_state = BleState.STANDBY
        self._zigbee = ZigbeeCore()

        self._init_handlers()

    def _init_handlers(self):
        for k, v in self._thread.get_handlers():
            self._transport.register_handler(v, k)
        for k, v in self._ble.get_handlers():
            self._transport.register_handler(v, k)
        for k, v in self._zigbee.get_handlers():
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
        return self._ble.get_address(self._transport)

    def get_node_id(self) -> bytes:
        return self._zigbee.get_state().node_id

    def get_zig_state(self) -> ZigbeeStatus:
        return self._zigbee.get_state()

    def join_network(self, channel: int):
        zig_cli.join_network(self._transport, channel)

    def leave_network(self):
        zig_cli.leave_network(self._transport)

    def start_throughput(self) -> bool:
        raise NotImplementedError()

    def wait_for_results(self) -> float:
        raise NotImplementedError()

    def get_dataset(self) -> ThreadNetworkData:
        return self._thread.get_dataset(self._transport)

    def get_ip_address(self) -> str:
        return self._thread.get_ip_address(self._transport)

    def factory_reset(self) -> None:
        self._thread.factory_reset(self._transport)

    def join_thread_network(self, channel: int, pan_id: bytes):
        self._thread.set_channel(self._transport, channel=channel)
        self._thread.set_pan_id(self._transport, pan_id=pan_id)
        self._thread.dataset_commit(self._transport)
        self._thread.start_network(self._transport)

    def get_thread_state(self) -> str:
        return self._thread.get_state(self._transport)

    def scan_results(self) -> set[bytes]:
        return self._ble.get_scan_results()
