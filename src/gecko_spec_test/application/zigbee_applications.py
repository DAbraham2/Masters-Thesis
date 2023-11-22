from gst_utils.gs_logging import get_logger
from interface.zigbee import ZigbeeUtils, ZigbeeCoordinator, ZigbeeThroughputable
from plugins.cli.zigbeee import ZigbeeCore, ZigbeeStatus, create_network
from transport import BaseTransport


class ZigbeeSoc(ZigbeeUtils, ZigbeeCoordinator, ZigbeeThroughputable):
    def __init__(self, transport: BaseTransport):
        self.logger = get_logger(__name__)
        self._transport = transport
        self._cli: ZigbeeCore = ZigbeeCore()
        self._state = None
        self._init_handlers()
        self._transport.start_connection()

    def _init_handlers(self):
        for k, v in self._cli.get_handlers().items():
            self._transport.register_handler(v, k)

    def get_node_id(self) -> bytes:
        return self._cli.get_state().node_id

    def get_zig_state(self) -> ZigbeeStatus:
        return self._cli.get_state()

    def create_network(self, channel: int, pan_id: bytes):
        create_network(self._transport, channel, pan_id, 0)

    def start_throughput(self) -> bool:
        raise NotImplementedError()

    def wait_for_results(self) -> float:
        raise NotImplementedError()

    def clean_up(self):
        ...
