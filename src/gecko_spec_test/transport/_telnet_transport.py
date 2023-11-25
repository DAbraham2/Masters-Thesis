import queue
import threading
import time
from threading import Thread
from queue import Queue
from telnetlib import Telnet
from typing import Callable, Optional

from gst_utils.gs_logging import Logger, get_logger
from .base_transport import BaseTransport

_LINE_TERM = '\r\n'


class ResponseNotFoundError(Exception):
    def __init__(self, command: str, expect: str):
        super().__init__(
            f'Response expected [{expect}] but not found for command: [{command}]'
        )


def _decode_for_log(msg: bytes) -> str:
    try:
        return msg.decode()
    except UnicodeDecodeError:
        return f'{msg}'


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

        self._queue: Queue = Queue(100)
        self._reader_thread: threading.Thread = Thread(
            target=self._parser_function, daemon=True
        )
        self._run = False
        self._handlers: dict[str, list[Callable[[str, str], None]]] = {}
        # self.send_and_expect('\n', '>', timeout=5)

    def __del__(self):
        """
        Deconstruct
        """
        self.logger.info('Deconstructing self...')
        if self._reader_thread.is_alive():
            self._run = False
            self._reader_thread.join(10)
        self._connection.close()
        self._connection = None

    def send(self, message: str) -> None:
        self.logger.debug('TX: [%s]', message)
        msg = message + '\n'
        msg = msg.encode('ascii')
        self._connection.write(msg)

    def send_and_expect(
        self, msg: str, expect: str, *, timeout: float = 15
    ) -> list[str] | str:
        checked_lines = []
        self._queue = Queue(100)
        self.send(msg)
        start_time = time.perf_counter_ns()
        current_time = start_time
        to = int(1_000_000_000 * timeout)
        while current_time - start_time < to:
            try:
                line = self._queue.get(timeout=0.1)
                checked_lines.append(line)
                if expect in line:
                    return checked_lines
            except queue.Empty:
                self.logger.info('Trying to send new line to cli...')
                self.send('')
                time.sleep(0.3)
                continue
            finally:
                current_time = time.perf_counter_ns()
        self.logger.critical('Timeout reached for command: [%s]...', msg)
        self.logger.debug('checked lines: <<%s>>', checked_lines)
        raise ResponseNotFoundError(msg, expect)

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
            arr.append(self._queue.get(True, None))

        return arr

    def start_connection(self) -> bool:
        self.logger.info('Connection starting...')
        self._connection.open(self.ip, self.port)
        self._run = True
        self._reader_thread.daemon = True
        self._reader_thread.start()
        self.send_and_expect('\n', '>', timeout=5)
        return True

    def stop_connection(self) -> bool:
        self.logger.info('Stopping connection...')
        self._run = False
        self._reader_thread.join(10)
        self._connection.close()
        self._handlers.clear()
        return True

    def _parser_function(self):
        term = _LINE_TERM.encode()
        left_out = b''
        while self._run:
            data = self._connection.read_until(term, timeout=0.3)
            if term not in data:
                left_out += data
                continue
            data += left_out
            left_out = b''
            try:
                lines = data.decode().strip().splitlines()
            except UnicodeDecodeError:
                self.logger.critical(f'unable to decode message: <<{data}>>')
                lines = []
            for line in lines[::-1]:
                clean = line.strip()
                if clean != '':
                    self.logger.debug('RX: [%s]', clean)
                    self._handler_task(clean)
                    self.__add_to_queue(clean)
            # self.logger.debug('Full RX: [%s]', _decode_for_log(data))

    def _handler_task(self, line: str) -> None:
        for k in self._handlers.keys():
            if k in line:
                for h in self._handlers[k]:
                    self.logger.debug('Found handler for [%s]', k)
                    h(line, k)

    def __add_to_queue(self, line: str) -> None:
        if 'Scan response' in line:
            return
        if self._queue.qsize() > 98:
            for _ in range(50):
                self._queue.get_nowait()

        self._queue.put(line, timeout=0.1)
