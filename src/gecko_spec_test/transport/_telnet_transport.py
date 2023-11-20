import threading
from threading import Thread
from queue import Queue
from telnetlib import Telnet
from typing import Callable, Optional

from gst_utils.logging import Logger, get_logger
from .base_transport import BaseTransport

_LINE_TERM = '\r\n'


def _decode_for_log(msg: bytes) -> str:
    return msg.decode()


class TelnetTransport(BaseTransport):
    def __init__(
        self,
        ip: str,
        port: int,
        *,
        connection: Optional[Telnet] = None,
        logger: Optional[Logger] = None,
    ):
        if connection is not None:
            self._connection = connection
        else:
            self.ip = ip
            self.port = port
            self._connection = Telnet(ip, port)

        if logger is None:
            self.logger = get_logger(f'telnet-cli-{ip}')
        else:
            self.logger = logger

        self.send_and_expect('\n', '>', timeout=5)

        self._queue: Queue = Queue(100)
        self._reader_thread: threading.Thread = Thread(
            target=self._parser_function, daemon=True
        )
        self._run = False
        self._handlers: dict[str, list[Callable[[str, str], None]]] = {}

    def __del__(self):
        """
        Deconstruct
        """
        self._run = False
        self._reader_thread.join(10)
        self._connection.close()
        self._connection = None

    def send(self, msg: str) -> None:
        self.logger.debug('TX: %s', msg)
        self._connection.write(bytes(msg + _LINE_TERM, 'ascii'))

    def send_and_expect(self, msg: str, expect: str, *, timeout: float = 1) -> str:
        self.send(msg)
        data = self._connection.read_until(expect.encode(), timeout)

        return data.decode()

    def register_handler(self, handler: Callable[[], None], expect: str) -> int:
        if expect not in self._handlers.keys():
            self._handlers[expect] = [handler]
        else:
            self._handlers[expect].append(handler)

        return 0

    def unregister_handler(self, handler_id: int) -> None:
        raise NotImplementedError()

    def receive(self) -> list[str]:
        arr = []
        siz = self._queue.qsize()
        for _ in range(siz):
            arr.append(self._queue.get_nowait())

        return arr

    def start_connection(self) -> bool:
        self._connection.open(self.ip, self.port)
        self.send_and_expect('\n', '>', timeout=5)
        self._run = True
        self._reader_thread.daemon = True
        self._reader_thread.start()
        return True

    def stop_connection(self) -> bool:
        self._run = False
        self._reader_thread.join(10)
        self._connection.close()
        self._handlers.clear()
        return True

    def _parser_function(self):
        term = _LINE_TERM.encode()
        left_out = b''
        while self._run:
            data = self._connection.read_until(term, timeout=0.2)
            if term not in data:
                left_out += data
                continue
            data += left_out
            left_out = b''
            lines = data.split(term)
            for l in lines[:-1]:
                line = l.decode().strip()
                if line != '':
                    self.logger.debug('RX: %s', line)
                    self._queue.put_nowait(line)
                    self._handler_task(line)
            self.logger.debug('Full RX: %s', _decode_for_log(data))

    def _handler_task(self, line: str) -> None:
        for k in self._handlers.keys():
            if k in line:
                for h in self._handlers[k]:
                    self.logger.debug('Found handler for %s', k)
                    h(line, k)
