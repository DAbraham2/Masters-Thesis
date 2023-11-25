from dataclasses import dataclass
from threading import Event
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
        self.on_info = Event()
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
        try:
            self._status.node_type = int(node[2:])
        except ValueError:
            self._status.node_type = -1

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
        self.on_info.set()

    def _handle_chan(self, actual: str, expected: str):
        """
        Example: `node [(>)3425B4FFFEA94A68] chan [14] pwr [3]\r\n`
        :param actual:
        :param expected:
        :return:
        """
        line = actual.split(expected)[1]
        self._status.channel = int(line.split(']')[0])

    def info(self, transport: BaseTransport):
        self.on_info.clear()
        transport.send_and_expect('info', 'network state')

    def get_state(self) -> ZigbeeStatus:
        if self._status is None and self.on_info.wait(0.5) is False:
            return ZigbeeStatus()
        return self._status


def _set_masks(transport: BaseTransport, channel: int) -> None:
    transport.send_and_expect('plugin network-steering mask set 1 0', 'Set')
    transport.send_and_expect('plugin network-steering mask set 2 0', 'Set')
    transport.send_and_expect(f'plugin network-steering mask add 1 {channel}', 'now')
    transport.send_and_expect(f'plugin network-steering mask add 2 {channel}', 'now')


def leave_network(transport: BaseTransport) -> None:
    transport.send_and_expect('network leave', 'leave 0x', timeout=5)


def __clear_keys(transport: BaseTransport) -> None:
    transport.send('keys clear')


def join_network(transport: BaseTransport, channel: int, distributed: int = 1):
    __clear_keys(transport)
    leave_network(transport)
    _set_masks(transport, channel)

    transport.send_and_expect(
        f'plugin network-steering start {distributed}', 'EMBER_NETWORK_UP', timeout=30
    )


def create_network(
    transport: BaseTransport, channel: int, pan_id: bytes, centralized: int
) -> bool:
    if centralized != 0 and centralized != 1:
        raise ValueError('centralized must be boolean')
    if len(pan_id) != 2:
        raise ValueError(f'invalid pan_id: [{pan_id.hex()}]')
    if channel < 0 or channel > 26:
        raise ValueError(f'invalid channel: [{channel}]')
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


def get_tp_counters(result: str) -> float:
    """Success messages: 10 out of 10"""
    s = result.split(':')[1]
    r = s.split('out of')
    success = int(r[0].strip())
    total = int(r[1].strip())

    return success / total


def send_data_to_remote(
    transport: BaseTransport,
    remote_node_id: bytes,
    *,
    packet_num: int = 10,
    interval: int = 2000,
    packet_size: int = 127,
    simultaneous_packets: int = 1,
    aps: int = 0,
    timeout: int = 400000,
) -> float:
    _ = transport.send_and_expect('option print-rx-msgs disable', 'disabled')
    _ = transport.send_and_expect(
        f'plugin throughput set-all 0x{remote_node_id.hex()} {packet_num} {interval} {packet_size} {simultaneous_packets} {aps} {timeout}',
        'PARAMETERS',
    )

    result = transport.send_and_expect('plugin throughput start', 'Success messages:')

    return get_tp_counters(result)
