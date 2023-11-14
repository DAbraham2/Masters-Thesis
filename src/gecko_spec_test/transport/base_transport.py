from typing import Protocol, Callable


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

    def send_and_expect(self, msg: str, expect: str) -> bool:
        """
        Send a message to a device and expect an output
        :param msg: content of the message
        :param expect: expected string
        :return: Returns `True` if expect is found. Else `False`.
        """
        ...

    def register_handler(self, handler: Callable[[], None], expect: str) -> int:
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


DEFAULT_TELNET_PORT = 9001


def transport_factory(device: str, remote_address: str) -> BaseTransport:
    from ._telnet_transport import TelnetTransport

    match device:
        case 'efr':
            return TelnetTransport(remote_address, DEFAULT_TELNET_PORT)
        case 'raspi':
            raise NotImplementedError()
        case other:
            raise NotImplementedError(f'command not implemented: {other}')
