from unittest.mock import Mock

import pytest
from transport._telnet_transport import TelnetTransport


@pytest.fixture()
def transport() -> (TelnetTransport, Mock):
    mock = Mock()
    return TelnetTransport('localhost', 23, connection=mock), mock


def test_send(transport: tuple[TelnetTransport, Mock]) -> None:
    dut, mock = transport
    message = 'henlo'
    dut.send(message)
    mock.write.assert_called_once_with(bytes(message, 'ascii'))


def test_receive_queue(transport: tuple[TelnetTransport, Mock]) -> None:
    dut, mock = transport

    dut.receive()
