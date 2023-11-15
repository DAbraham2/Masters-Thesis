from threading import Event
from typing import Callable, Optional

from transport import BaseTransport
from interface.ot import ThreadNetworkData
from gst_utils.logging import get_logger

logger = get_logger(__name__)


class OtUpCli:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.__handlers = {
            'Channel:': self._handle_channel,
            'PAN ID:': self._handle_pan_id,
            'Ext PAN ID:': None,
            'Network Key:': None,
            'Network Name:': None,
            'IP address:': None,
        }
        self._dataset_event: Event = Event()
        self._dataset: Optional[ThreadNetworkData] = None

        self._ip_address: str = ''
        self._ip_address_event: Event = Event()

    def get_handlers(self) -> dict[str, Callable[[str, str], None]]:
        return self.__handlers

    @staticmethod
    def factory_reset(transport: BaseTransport):
        transport.send('factory_reset')

    @staticmethod
    def dataset_new(transport: BaseTransport):
        transport.send_and_expect('dataset_new', 'Status:')

    @staticmethod
    def dataset_commit(transport: BaseTransport):
        transport.send_and_expect('dataset_commit_active', 'Status:')

    @staticmethod
    def set_channel(transport: BaseTransport, *, channel: int) -> None:
        logger.debug('set_channel with channelId: %s', channel)

    @staticmethod
    def set_network_key(transport: BaseTransport, *, network_key: bytes) -> None:
        logger.debug('set_network_key with network_key: 0x%s', network_key.hex())

    @staticmethod
    def set_pan_id(transport: BaseTransport, *, pan_id: bytes) -> None:
        logger.debug('set_pan_id with pan_id: 0x%s', pan_id.hex())

    def get_ip_address(self, transport: BaseTransport) -> str:
        self.logger.debug('get_ip_address')
        if self._ip_address != '':
            self.logger.info('using previous ip: %s', self._ip_address)
            return self._ip_address
        self._ip_address_event.clear()
        transport.send('thread_ipaddr')
        self._ip_address_event.wait(10.0)
        return self._ip_address

    def get_dataset(self, transport: BaseTransport) -> ThreadNetworkData:
        self.logger.debug('get_dataset')
        transport.send('dataset')

        return self._dataset

    def _handle_channel(self, actual: str, expected: str) -> None:
        self.logger.debug(
            '_handle_channel with actual: %s and expected: %s', actual, expected
        )
        channel = actual
        if actual.startswith(expected):
            channel = channel.removeprefix(expected)
        channel = channel.strip()
        try:
            chn = int(channel)
            if self._dataset is None:
                self._dataset = ThreadNetworkData(bytes(), bytes(), '', chn)
            self._dataset.channel = chn
        except ValueError:
            self.logger.error('Found channel {%s} is not an integer!', channel)

    def _handle_pan_id(self, actual: str, expected: str) -> None:
        self.logger.debug(
            '_handle_pan_id with actual: %s and expected: %s', actual, expected
        )
        pan = actual
        if actual.startswith(expected):
            pan = pan.removeprefix(expected)
        pan = pan.strip()
        b = bytes.fromhex(pan.removeprefix('0x'))
        if self._dataset is None:
            self._dataset = ThreadNetworkData(b, bytes(16), '', -1)

        self._dataset.pan_id = b

    def _handle_ip_addr(self, actual: str, expected: str) -> None:
        self.logger.debug(
            '_handle_ip_addr with actual: %s and expected: %s', actual, expected
        )
        addr = actual
        if actual.startswith(expected):
            addr = addr.removeprefix(expected)
        addr.strip()
        self._ip_address = addr
        self._ip_address_event.set()

    def _handle_nwk_key(self, actual: str, expected: str) -> None:
        ...

    def _handle_nwk_name(self, actual: str, expected: str) -> None:
        ...


class ZigbeeBleDmpCli:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.__handlers = {
            'BLE address:': self._handle_address,
        }

    def get_handlers(self) -> dict[str, Callable[[str, str], None]]:
        return self.__handlers

    def _handle_address(self, actual, expected) -> None:
        ...

    def enter_connectable(
        self,
        transport: BaseTransport,
        *,
        adv_handle: int,
        discovery_mode: int,
        connectable_mode: int,
    ):
        ...

    def stop_advertise(self, transport: BaseTransport, *, handle: int):
        ...

    def start_scan(self, transport: BaseTransport, *, discovery_mode: int):
        ...

    def stop_scan(self, transport: BaseTransport):
        ...

    def scan_config(
        self, transport: BaseTransport, *, mode: int, interval: int, window: int
    ):
        ...

    def get_address(self, transport: BaseTransport):
        ...

    def hello(self, transport: BaseTransport):
        ...
