from gst_utils.logging import get_logger
from interface.zigbee import ZigbeeUtils, ZigbeeCoordinator, ZigbeeThroughputable
from transport import BaseTransport


class ZigbeeSoc(ZigbeeUtils, ZigbeeCoordinator, ZigbeeThroughputable):
    def __init__(self, transport: BaseTransport):
        self.logger = get_logger(__name__)
        self._transport = transport
        self._cli = None
        self._state = None

    def _init_handlers(self):
        for k, v in self._cli.get_handlers():
            self._transport.register_handler(v, k)

    def get_node_id(self) -> bytes:
        return super().get_node_id()

    def create_network(self):
        super().create_network()

    def start_throughput(self) -> bool:
        return super().start_throughput()

    def wait_for_results(self) -> float:
        return super().wait_for_results()

    def clean_up(self):
        ...
