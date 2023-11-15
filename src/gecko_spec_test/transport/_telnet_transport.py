from queue import Queue
from telnetlib import Telnet
from typing import Callable, Optional

from .base_transport import BaseTransport


class TelnetTransport(BaseTransport):
    def __init__(self, ip: str, port: int, *, connection: Optional[Telnet] = None):
        if connection is not None:
            self._connection = connection
        else:
            self._connection = Telnet(ip, port)

        self._queue: Queue = Queue(100)

    def send(self, msg: str) -> None:
        self._connection.write(bytes(msg, 'ascii'))

    def send_and_expect(self, msg: str, expect: str) -> str:
        raise NotImplementedError()

    def register_handler(self, handler: Callable[[], None], expect: str) -> int:
        raise NotImplementedError()

    def unregister_handler(self, handler_id: int) -> None:
        raise NotImplementedError()

    def receive(self) -> list[str]:
        raise NotImplementedError()

    def start_connection(self) -> bool:
        raise NotImplementedError()

    def stop_connection(self) -> bool:
        raise NotImplementedError()
