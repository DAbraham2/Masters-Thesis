from typing import Optional

from gst_utils.gs_logging import get_logger
from transport import BaseTransport
from interface.ot import ThreadNetworkData, ThreadUtils, ThreadCoordinator
from plugins.cli.open_thread import OtFtdCli
import plugins.cli.open_thread as open_thread

logger = get_logger(__name__)


class OtFtdSoc(ThreadUtils, ThreadCoordinator):
    def __init__(self, transport: BaseTransport):
        self._transport = transport
        self._cli = OtFtdCli()
        self.__init_handlers()
        self._transport.start_connection()

    def __init_handlers(self):
        for k, v in self._cli.get_handlers().items():
            self._transport.register_handler(v, k)

    def create_network(
        self, *, channel: Optional[int] = None, pan_id: Optional[bytes] = None
    ) -> None:
        if channel is None or pan_id is None:
            open_thread.create_new_network(self._transport)
        else:
            open_thread.create_network(self._transport, channel, pan_id)

    def get_dataset(self) -> ThreadNetworkData:
        return self._cli.dataset(self._transport)

    def ping(self, remote_address: str) -> None:
        open_thread.ping(self._transport, remote_address)

    def get_ip_address(self) -> str:
        return open_thread.ip_address(self._transport)

    def factory_reset(self) -> None:
        self._cli.factory_reset(self._transport)
