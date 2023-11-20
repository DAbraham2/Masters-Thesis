from dataclasses import dataclass
from typing import Callable

from transport import BaseTransport


@dataclass
class ZigbeeStatus:
    channel: int = -1
    pan_id: bytes = bytes(2)
    node_id: bytes = bytes(2)
    node_type: int = -1
    network_state: int = -1


class ZigbeeCore:
    def __init__(self):
        self._status: ZigbeeStatus = ZigbeeStatus()
        self.__handlers: dict[str, Callable[[str, str], None]] = {
            'panID [': self._handle_pan_id,
            'nodeType [': self._handle_node_type,
            'network state [': self._handle_nwk_state,
            'chan [': self._handle_chan,
        }

    def get_handlers(self) -> dict[str, Callable[[str, str], None]]:
        return self.__handlers

    def _handle_pan_id(self, actual: str, expected: str):
        """
        Example: `panID [0xD485] nodeID [0x5D3A] xpan [0x(>)9D4BA0E1C4E24011]\r\n`
        :param actual:
        :param expected:
        :return:
        """
        line = ''
        if actual.startswith(expected):
            line = actual.removeprefix(expected)
        else:
            line = actual.split(expected)[1]

        tokens = line.split(' ')
        pan = tokens[0].removesuffix(']')
        self._status.pan_id = bytes.fromhex(pan[2:])

        node = tokens[2].removeprefix('[').removesuffix(']')
        self._status.node_id = bytes.fromhex(node[2:])

    def _handle_node_type(self, actual: str, expected: str):
        """
        Example: `nodeType [0x02]\r\n`
        :param actual:
        :param expected:
        :return:
        """
        line = ''
        if actual.startswith(expected):
            line = actual.removeprefix(expected)
        else:
            line = actual.split(expected)[1]

        node = line.split(']')[0]
        self._status.node_type = int(node[2:])

    def _handle_nwk_state(self, actual: str, expected: str):
        """
        Example: `network state [02] Buffs: 75 / 75\r\n`
        :param actual:
        :param expected:
        :return:
        """
        line = ''
        if actual.startswith(expected):
            line = actual.removeprefix(expected)
        else:
            line = actual.split(expected)[1]

        nwk = line.split(']')[0]
        self._status.network_state = int(nwk)

    def _handle_chan(self, actual: str, expected: str):
        """
        Example: `node [(>)3425B4FFFEA94A68] chan [14] pwr [3]\r\n`
        :param actual:
        :param expected:
        :return:
        """
        line = actual.split(expected)[1]
        self._status.channel = int(line.split(']')[0])

    @staticmethod
    def info(transport: BaseTransport):
        transport.send('info')

    def get_state(self) -> ZigbeeStatus:
        return self._status


def _set_masks(transport: BaseTransport, channel: int) -> None:
    transport.send_and_expect('plugin network-steering mask set 1 0', 'Set')
    transport.send_and_expect('plugin network-steering mask set 2 0', 'Set')
    transport.send_and_expect(f'plugin network-steering mask set 1 {channel}', 'Set')
    transport.send_and_expect(f'plugin network-steering mask set 2 {channel}', 'Set')


def leave_network(transport: BaseTransport) -> None:
    transport.send_and_expect('leave network', 'leave 0x')


def join_network(transport: BaseTransport, channel: int, distributed: int = 1):
    leave_network(transport)
    _set_masks(transport, channel)

    transport.send_and_expect(
        f'plugin network-steering start {distributed}', 'EMBER_NETWORK_UP', timeout=10
    )


def create_network(
    transport: BaseTransport, channel: int, pan_id: bytes, centralized: int
) -> bool:
    if centralized != 0 or centralized != 1:
        raise ValueError('centralized must be boolean')
    if len(pan_id) != 2:
        raise ValueError('invalid pan_id')
    if channel < 0 or channel > 17:
        raise ValueError('invalid channel')
    leave_network(transport)
    transport.send_and_expect(
        f'plugin network-creator form {centralized} 0x{pan_id.hex().upper()} 3 {channel}',
        'EMBER_NETWORK_UP',
        timeout=10,
    )

    transport.send_and_expect(
        'plugin network-creator-security open-network',
        'EMBER_NETWORK_OPENED',
        timeout=10,
    )

    return True
