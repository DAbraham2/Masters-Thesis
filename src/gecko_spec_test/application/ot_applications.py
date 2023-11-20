from transport import BaseTransport


class OtFtdSoc:
    def __init__(self, transport: BaseTransport):
        self._transport = transport
