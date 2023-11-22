from typing import Protocol, Callable, Optional

from gst_utils.gs_logging import get_logger


class BaseTransport(Protocol):
    """
    A base class for transport layer
    """

    def send(self, msg: str) -> None:
        """
        Send a string message to a device
        :param msg: content of the message
        :return: None
        """
        ...

    def send_and_expect(self, msg: str, expect: str, *, timeout: float = 1) -> str:
        """
        Send a message to a device and expect an output
        :param timeout:
        :param msg: content of the message
        :param expect: expected string
        :return: Returns the expected line
        """
        ...

    def register_handler(self, handler: Callable[[str, str], None], expect: str) -> int:
        """
        Append an event handler to a transport stream.
        :param expect: expected event to run handler on
        :param handler: handler function
        :return: handler id
        """
        ...

    def unregister_handler(self, handler_id: int) -> None:
        """
        Remove a handler
        :param handler_id: given handler
        :return: None
        """
        ...

    def receive(self) -> list[str]:
        """
        Retrieve the input lines from the stream
        :return: received lines
        """
        ...

    def start_connection(self) -> bool:
        ...

    def stop_connection(self) -> bool:
        ...


DEFAULT_TELNET_PORT = 4901


def transport_factory(
    device: str, remote_address: str, *, application_name: Optional[str] = None
) -> BaseTransport:
    from ._telnet_transport import TelnetTransport

    logger = None
    if application_name is not None:
        logger = get_logger(f'{application_name}-cli-{remote_address}')
    match device:
        case 'efr':
            return TelnetTransport(remote_address, DEFAULT_TELNET_PORT, logger=logger)
        case 'raspi':
            raise NotImplementedError()
        case other:
            raise NotImplementedError(f'command not implemented: {other}')
