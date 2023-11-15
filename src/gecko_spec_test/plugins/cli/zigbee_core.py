from transport import BaseTransport


def info(transport: BaseTransport):
    transport.send_and_expect('info', 'network state')


def reset(transport: BaseTransport):
    transport.send('reset')


def version(transport: BaseTransport) -> str:
    line = transport.send_and_expect('version', 'stack ver.')
    return line.removeprefix('stack ver.').strip()


def events(transport: BaseTransport):
    ...
