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
        self._ble = ZigbeeBleDmpCli(
            on_external_join=self.__ble_peri_join, on_external_disc=self.__ble_peri_disc
        )
        self._ble_state = BleState.STANDBY
        self._zigbee = ZigbeeCore()

        self._init_handlers()

        self._transport.start_connection()

    def __del__(self):
        del self._transport

    def _init_handlers(self):
        for k, v in self._thread.get_handlers().items():
            self._transport.register_handler(v, k)
        for k, v in self._ble.get_handlers().items():
            self._transport.register_handler(v, k)
        for k, v in self._zigbee.get_handlers().items():
            self._transport.register_handler(v, k)

    def start_scanning(self) -> bool:
        try:
            self._ble.start_scan(self._transport, discovery_mode=0x2)
            self._ble_state = BleState.SCANNING
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
        self._zigbee.info(self._transport)
        return self._zigbee.get_state()

    def join_network(self, channel: int):
        zig_cli.join_network(self._transport, channel)

    def leave_network(self):
        zig_cli.leave_network(self._transport)

    def start_throughput(self, remote_node_id: bytes) -> float:
        return zig_cli.send_data_to_remote(self._transport, remote_node_id)

    def get_dataset(self) -> ThreadNetworkData:
        return self._thread.get_dataset(self._transport)

    def get_ip_address(self) -> str:
        return self._thread.get_ip_address(self._transport)

    def factory_reset(self) -> None:
        setattr(self._ble, '_in_scan', False)
        self._thread.factory_reset(self._transport)
        self._transport.send_and_expect('', '>')

    def join_thread_network(self, channel: int, pan_id: bytes):
        self._thread.set_channel(self._transport, channel=channel)
        self._thread.set_pan_id(self._transport, pan_id=pan_id)
        self._thread.dataset_commit(self._transport)
        self._thread.start_network(self._transport)

    def join_network_with_nwk_key(self, network_key: bytes):
        self._thread.set_network_key(self._transport, network_key=network_key)
        self._thread.dataset_commit(self._transport)
        self._thread.start_network(self._transport)

    def get_thread_state(self) -> str:
        return self._thread.get_state(self._transport)

    def scan_results(self) -> set[bytes]:
        return self._ble.get_scan_results()

    def say_hello(self) -> None:
        self._ble.hello(self._transport)

    def ping(self, remote_address: str) -> None:
        self._thread.ping(self._transport, remote_address)

    def __ble_peri_join(self) -> None:
        self._ble_state = BleState.CONNECTION

    def __ble_peri_disc(self) -> None:
        self._ble_state = BleState.STANDBY
