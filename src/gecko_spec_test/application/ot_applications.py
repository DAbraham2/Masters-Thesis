from gst_utils.logging import get_logger
from transport import BaseTransport
from interface.ot import ThreadNetworkData
from plugins.cli.open_thread import OtFtdCli
import plugins.cli.open_thread as open_thread

logger = get_logger(__name__)


class OtFtdSoc:
    def __init__(self, transport: BaseTransport):
        self._transport = transport
        self._cli = OtFtdCli()
        self.__init_handlers()

    def __init_handlers(self):
        for k, v in self._cli.get_handlers():
            self._transport.register_handler(v, k)

    def create_new_network(self) -> None:
        open_thread.create_new_network(self._transport)

    def create_network(self, channel: int, pan_id: bytes) -> None:
        open_thread.create_network(self._transport, channel, pan_id)

    def dataset(self) -> ThreadNetworkData:
        return self._cli.dataset(self._transport)

    def ping(self, remote_address: str) -> None:
        open_thread.ping(self._transport, remote_address)

    def get_ip_address(self) -> str:
        return open_thread.ip_address(self._transport)
