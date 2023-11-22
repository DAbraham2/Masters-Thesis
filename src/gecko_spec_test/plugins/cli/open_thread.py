from gst_utils.gs_logging import get_logger
from interface.ot import ThreadNetworkData
from transport import BaseTransport

logger = get_logger(__name__)


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
    transport.send_and_expect('dataset clear', 'Done')
    transport.send_and_expect('dataset init new', 'Done')
    transport.send_and_expect('dataset commit active', 'Done')
    transport.send_and_expect('ifconfig up', 'Done')
    transport.send('thread start')


def create_network(transport: BaseTransport, channel: int, pan_id: bytes):
    transport.send_and_expect('dataset clear', 'Done')
    transport.send_and_expect(f'dataset channel {channel}', 'Done')
    transport.send_and_expect(f'dataset panid 0x{pan_id.hex()}', 'Done')
    transport.send_and_expect('dataset commit active', 'Done')
    transport.send_and_expect('ifconfig up', 'Done')
    transport.send('thread start')


class OtFtdCli:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.__handlers = {
            'Channel:': self.__handle_chn,
            'PAN ID:': self.__handle_pan,
            'Network Key:': self.__handle_nwk_key,
            'Network Name:': self.__handle_nwk_name,
        }
        self._dataset = ThreadNetworkData()

    def __handle_chn(self, actual: str, expected: str) -> None:
        line = actual.removeprefix(expected).strip()
        self._dataset.channel = int(line)

    def __handle_pan(self, actual: str, expected: str) -> None:
        line = actual.removeprefix(expected).strip()
        self._dataset.pan_id = bytes.fromhex(line[2:])

    def __handle_nwk_key(self, actual: str, expected: str) -> None:
        line = actual.removeprefix(expected).strip()
        self._dataset.network_key = bytes.fromhex(line)

    def __handle_nwk_name(self, actual: str, expected: str) -> None:
        line = actual.removeprefix(expected).strip()
        self._dataset.network_name = line

    def get_handlers(self):
        return self.__handlers

    def dataset(self, transport: BaseTransport) -> ThreadNetworkData:
        if self._dataset.channel == -1:
            transport.send_and_expect('dataset active', 'Done')

        return self._dataset

    @staticmethod
    def get_state(transport: BaseTransport) -> str:
        result = transport.send_and_expect('state', 'Done')

        return result

    def reset_network(self, transport: BaseTransport) -> None:
        transport.send_and_expect('thread stop', 'Done')
        self._dataset = ThreadNetworkData()

    def factory_reset(self, transport: BaseTransport) -> None:
        transport.send('factory reset')
        self._dataset = ThreadNetworkData()
