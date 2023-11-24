import time
from threading import Event
from typing import Callable, Optional

from tenacity import retry, stop_after_attempt, wait_random_exponential

from gst_utils.ot_utils import _is_state
from transport import BaseTransport
from interface.ot import ThreadNetworkData
from gst_utils.gs_logging import get_logger
from gst_utils.cleaner import clean_cli_command

logger = get_logger(__name__)


class OtUpCli:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.__handlers: dict[str, Callable[[str, str], None]] = {
            'Channel:': self._handle_channel,
            'PAN ID:': self._handle_pan_id,
            'Network Key:': self._handle_nwk_key,
            'Network Name:': self._handle_nwk_name,
            'IP address:': self._handle_ip_addr,
        }
        self._dataset_event: Event = Event()
        self._dataset: Optional[ThreadNetworkData] = None

        self._ip_address: str = ''
        self._ip_address_event: Event = Event()

    def get_handlers(self) -> dict[str, Callable[[str, str], None]]:
        return self.__handlers

    @staticmethod
    def factory_reset(transport: BaseTransport):
        transport.send_and_expect('factory_reset', 'Reset info:', timeout=5)

    @staticmethod
    def dataset_new(transport: BaseTransport):
        transport.send_and_expect('dataset_new', 'Status:')

    @staticmethod
    def dataset_commit(transport: BaseTransport):
        transport.send_and_expect('dataset_commit_active', 'Status:')

    @staticmethod
    def set_channel(transport: BaseTransport, *, channel: int) -> None:
        transport.send(f'dataset_channel {channel}')

    @staticmethod
    def set_network_key(transport: BaseTransport, *, network_key: bytes) -> None:
        transport.send(f'dataset_networkkey {{{network_key.hex()}}}')

    @staticmethod
    def set_pan_id(transport: BaseTransport, *, pan_id: bytes) -> None:
        transport.send(f'dataset_pan_id 0x{pan_id.hex()}')

    @staticmethod
    def ping(transport: BaseTransport, remote_address: str) -> None:
        transport.send_and_expect(f'ping_ipaddr {remote_address}', 'Status: 0x0')

    @staticmethod
    def start_network(transport: BaseTransport) -> None:
        transport.send_and_expect('ifconfig_up', 'Status: 0x0')
        transport.send_and_expect('thread_start', 'Status: 0x0')
        time.sleep(0.5)

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

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=10, multiplier=0.1),
    )
    def get_state(self, transport: BaseTransport) -> str:
        transport.send('thread_state')
        time.sleep(0.3)
        lines = transport.receive()
        self.logger.debug('get_state receive_queue: %s', lines)
        for line in lines:
            if _is_state(line.strip()):
                return line.strip()

        raise ValueError('state did not got here...')

    def _handle_channel(self, actual: str, expected: str) -> None:
        self.logger.debug(
            '_handle_channel with actual: %s and expected: %s', actual, expected
        )
        channel = clean_cli_command(actual, expected)
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
        pan = clean_cli_command(actual, expected)
        b = bytes.fromhex(pan.removeprefix('0x'))
        if self._dataset is None:
            self._dataset = ThreadNetworkData(b, bytes(16), '', -1)

        self._dataset.pan_id = b

    def _handle_ip_addr(self, actual: str, expected: str) -> None:
        self.logger.debug(
            '_handle_ip_addr with actual: %s and expected: %s', actual, expected
        )
        addr = clean_cli_command(actual, expected)
        self._ip_address = addr
        self._ip_address_event.set()

    def _handle_nwk_key(self, actual: str, expected: str) -> None:
        self.logger.debug(
            '_handle_nwk_key Actual: [%s] -- Expected: [%s]', actual, expected
        )
        line = clean_cli_command(actual, expected)
        self._dataset.network_key = bytes.fromhex(line)

    def _handle_nwk_name(self, actual: str, expected: str) -> None:
        self.logger.debug(
            '_handle_nwk_name Actual: [%s] -- Expected: [%s]', actual, expected
        )
        line = actual.removeprefix(expected).strip()
        self._dataset.network_name = line


def _bytes_from_ble_address(original: str) -> bytes:
    """
    Turns ble addresses to bytes
    :param original: given address `example: [34 25 B4 A9 4A 66]`
    :return:
    """
    logger.debug('Actual: <%s>', original)
    cleaned = ''
    if original.removeprefix('['):
        cleaned = original.removeprefix('[').removesuffix(']').strip()
    try:
        cleaned = cleaned.lower()
        return bytes.fromhex(cleaned)
    except ValueError:
        logger.critical('Could not convert address to bytes: <<%s>>', original)
        return bytes(6)


def _ble_address_from_bytes(original: bytes) -> str:
    """
    Turns bytes to cli compatible hex
    :param original:
    :return:
    """
    return f'{{{original.hex()}}}'


class ZigbeeBleDmpCli:
    def __init__(
        self,
        *,
        on_external_join: Optional[Callable] = None,
        on_external_disc: Optional[Callable] = None,
    ):
        self.logger = get_logger(__name__)
        self.__handlers = {
            'BLE address:': self._handle_address,
            'BLE connection opened': self._handle_conn_opened,
            'BLE connection closed': self.__handle_conn_closed,
        }
        self._peripheral: bool = False
        self._in_scan: bool = False
        self._scan_result: set[bytes] = set()
        self._address: bytes = bytes(6)
        self.__on_external_join = on_external_join
        self.__on_external_disconn = on_external_disc

    def get_handlers(self) -> dict[str, Callable[[str, str], None]]:
        return self.__handlers

    def _handle_address(self, actual: str, expected: str) -> None:
        """
        Actual example: `BLE address: [34 25 B4 A9 4A 66]`
        :param actual:
        :param expected:
        :return:
        """
        self.logger.debug(
            '_handle_address Actual: [%s] -- Expected: [%s]', actual, expected
        )
        data = clean_cli_command(actual, expected)
        match self._in_scan:
            case True:
                self.logger.debug('Adding to scans...')
                self._scan_result.add(_bytes_from_ble_address(data))
            case False:
                self._address = _bytes_from_ble_address(data)

    def _handle_conn_opened(self, actual, expected) -> None:
        self.logger.debug(
            '_handle_conn_opened Actual: [%s] -- Expected: [%s]', actual, expected
        )
        if self.__on_external_join is not None:
            self.__on_external_join()

    def __handle_conn_closed(self, actual: str, expected: str) -> None:
        self.logger.debug(
            '__handle_conn_closed Actual: [%s] -- Expected: [%s]', actual, expected
        )
        if self.__on_external_disconn is not None:
            self.__on_external_disconn()

    def enter_connectable(
        self,
        transport: BaseTransport,
        *,
        adv_handle: int,
        discovery_mode: int,
        connectable_mode: int,
    ):
        transport.send_and_expect(
            f'plugin ble gap set-mode {adv_handle} {discovery_mode} {connectable_mode}',
            expect='success',
        )

    @staticmethod
    def stop_advertise(transport: BaseTransport, *, handle: int):
        transport.send_and_expect(
            f'plugin ble gap stop-advertising {handle}', 'success'
        )

    def start_scan(self, transport: BaseTransport, *, discovery_mode: int):
        if discovery_mode < 0 or discovery_mode > 2:
            raise ValueError('discovery_mode shall be between 0 and 2')
        self._scan_result = set()
        self._in_scan = True
        transport.send_and_expect(
            f'plugin ble gap start-scan {discovery_mode}', 'success'
        )

    def stop_scan(self, transport: BaseTransport):
        transport.send_and_expect('plugin ble gap stop-scan', 'success')
        self._in_scan = False

    def scan_config(
        self, transport: BaseTransport, *, mode: int, interval: int, window: int
    ):
        raise NotImplementedError()

    def get_address(self, transport: BaseTransport) -> bytes:
        if self._address != bytes(6):
            return self._address

        transport.send('plugin ble get address')
        for _ in range(10):
            if self._address != bytes(6):
                return self._address
            time.sleep(0.4)

    def get_scan_results(self):
        return self._scan_result

    @staticmethod
    def hello(transport: BaseTransport):
        transport.send_and_expect('plugin ble hello', 'success', timeout=5)
