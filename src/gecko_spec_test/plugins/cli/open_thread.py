import time
from threading import Event

from gst_utils.cleaner import clean_cli_command
from gst_utils.gs_logging import get_logger
from gst_utils.ot_utils import _is_state
from interface.ot import ThreadNetworkData
from transport import BaseTransport

logger = get_logger(__name__)


class NetworkStartTimeout(Exception):
    ...


def ping(transport: BaseTransport, remote_address: str) -> None:
    """
    Ping another device through thread network
    :param transport:
    :param remote_address:
    :return:
    """
    result = transport.send_and_expect(f'ping {remote_address} 50 1 2000', 'Done')
    logger.debug('\n\nping result: %s\n\n', result)


def ip_address(transport: BaseTransport) -> str:
    result = transport.send_and_expect('ipaddr linklocal', 'Done')
    return result


def create_new_network(transport: BaseTransport):
    _ = transport.send_and_expect('dataset clear', 'Done')
    _ = transport.send_and_expect('dataset init new', 'Done')
    _ = transport.send_and_expect('dataset commit active', 'Done')
    _ = transport.send_and_expect('ifconfig up', 'Done')
    transport.send('thread start')


def create_network(transport: BaseTransport, channel: int, pan_id: bytes):
    _ = transport.send_and_expect('dataset clear', 'Done')
    _ = transport.send_and_expect(f'dataset channel {channel}', 'Done')
    _ = transport.send_and_expect(f'dataset panid 0x{pan_id.hex()}', 'Done')
    _ = transport.send_and_expect('dataset commit active', 'Done')
    _ = transport.send_and_expect('ifconfig up', 'Done')
    transport.send('thread start')


class OtFtdCli:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.__handlers = {
            'Channel:': self.__handle_chn,
            'PAN ID:': self.__handle_pan,
            'Network Key:': self.__handle_nwk_key,
            'Network Name:': self.__handle_nwk_name,
            '[N] Mle-----------: Role': self.__handle_role_change,
        }
        self.__state = 'disabled'
        self.__leader_event = Event()
        self._dataset = ThreadNetworkData()

    def __handle_chn(self, actual: str, expected: str) -> None:
        line = actual.removeprefix(expected).strip()
        self._dataset.channel = int(line)

    def __handle_pan(self, actual: str, expected: str) -> None:
        if 'Ext PAN ID' not in actual:
            line = actual.removeprefix(expected).strip()
            self._dataset.pan_id = bytes.fromhex(line[2:])

    def __handle_nwk_key(self, actual: str, expected: str) -> None:
        line = actual.removeprefix(expected).strip()
        self._dataset.network_key = bytes.fromhex(line)

    def __handle_nwk_name(self, actual: str, expected: str) -> None:
        line = actual.removeprefix(expected).strip()
        self._dataset.network_name = line

    def __handle_role_change(self, actual: str, expected: str) -> None:
        """
        [N] Mle-----------: Role leader -> detached
        :param actual:
        :param expected:
        :return:
        """
        line = clean_cli_command(actual, expected)
        states = line.split('->')
        self.logger.debug(
            'Changed internal state from [%s] to [%s]', states[0], states[1]
        )
        self.__state = states[1].strip()
        if self.__state == 'leader':
            self.__leader_event.set()
        elif states[0].strip() == 'leader':
            self.__leader_event.clear()

    def get_handlers(self):
        return self.__handlers

    def dataset(self, transport: BaseTransport) -> ThreadNetworkData:
        if self._dataset.channel == -1:
            transport.send_and_expect('dataset active', 'Done')

        return self._dataset

    def get_state(self, transport: BaseTransport) -> str:
        return self.__state

    def reset_network(self, transport: BaseTransport) -> None:
        transport.send_and_expect('thread stop', 'Done')
        self._dataset = ThreadNetworkData()

    def factory_reset(self, transport: BaseTransport) -> None:
        transport.send('reset')
        self._dataset = ThreadNetworkData()
        time.sleep(2)

    def wait_for_network_start(self, timeout: float = 15):
        res = self.__leader_event.wait(timeout)
        if res is False:
            raise NetworkStartTimeout()
