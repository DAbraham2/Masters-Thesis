from queue import Queue
from typing import Callable

from gst_utils.gs_logging import get_logger
from transport import BaseTransport


class MockedTransport(BaseTransport):
    def __init__(self):
        self.logger = get_logger(__name__)
        self._queue = Queue()
        self._handlers: dict[str, list[Callable[[str, str], None]]] = {}

    def send(self, msg: str) -> None:
        self._queue.put(msg)
        match msg:
            case 'dataset':
                self._find_and_trigger('Channel:', '14')
                self._find_and_trigger(
                    'Network Key:', 'AB BA EF FE 00 11 22 33 44 55 66'
                )
                self._find_and_trigger('Network Name:', 'Test network')
                self._find_and_trigger('PAN ID:', '0x' + b'\x04\x20'.hex().upper())

            case default:
                self.logger.warning('Command %s not implemented...', default)

    def send_and_expect(self, msg: str, expect: str, *, timeout=1) -> str:
        return super().send_and_expect(msg, expect)

    def register_handler(self, handler: Callable[[str, str], None], expect: str) -> int:
        if self._handlers.get(expect) is None:
            self._handlers[expect] = list([handler])
            return 1

        self._handlers[expect].append(handler)

        return 0

    def unregister_handler(self, handler_id: int) -> None:
        ...

    def receive(self) -> list[str]:
        self.logger.debug('receive')
        return self._queue.get_nowait()

    def start_connection(self) -> bool:
        ...

    def stop_connection(self) -> bool:
        ...

    def _find_handlers(self, expect: str) -> list[Callable[[str, str], None]]:
        return self._handlers.get(expect)

    def _find_and_trigger(self, expect: str, value: str) -> None:
        hs = self._find_handlers(expect)
        for h in hs:
            if h is not None:
                h(f'{expect} {value}', expect)
