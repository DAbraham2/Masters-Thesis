import time

from gst_utils.gs_logging import get_logger
from interface.zigbee import ZigbeeUtils, ZigbeeCoordinator, ZigbeeThroughputable
from plugins.cli.zigbeee import ZigbeeCore, ZigbeeStatus, create_network
from transport import BaseTransport
import plugins.cli.zigbeee as zig_cli


class ZigbeeSoc(ZigbeeUtils, ZigbeeCoordinator, ZigbeeThroughputable):
    def __init__(self, transport: BaseTransport):
        self.logger = get_logger(__name__)
        self._transport = transport
        self._cli: ZigbeeCore = ZigbeeCore()
        self._state = None
        self._init_handlers()
        self._transport.start_connection()

    def __del__(self):
        del self._transport

    def _init_handlers(self):
        for k, v in self._cli.get_handlers().items():
            self._transport.register_handler(v, k)

    def get_node_id(self) -> bytes:
        return self._cli.get_state().node_id

    def get_zig_state(self) -> ZigbeeStatus:
        self._cli.info(self._transport)
        time.sleep(0.3)
        return self._cli.get_state()

    def create_network(self, channel: int, pan_id: bytes):
        create_network(self._transport, channel, pan_id, 0)

    def start_throughput(self, remote_node_id: bytes) -> float:
        return zig_cli.send_data_to_remote(self._transport, remote_node_id)

    def reset(self):
        zig_cli.leave_network(self._transport)
