import random

import pytest

from interface.ot import ThreadNetworkData
from transport import BaseTransport
from plugins.soc import OtUpCli
from .stubs.transport import MockedTransport


@pytest.fixture()
def stub() -> BaseTransport:
    return MockedTransport()


@pytest.fixture()
def cli_factory(stub) -> OtUpCli:
    x = OtUpCli()
    h = x.get_handlers()
    for k, v in h.items():
        stub.register_handler(v, k)

    return x


def test_pan_handler(cli_factory) -> None:
    cli = cli_factory

    m = getattr(cli, '_handle_pan_id')
    m('PAN ID: 0xABBA', 'PAN ID:')
    d: ThreadNetworkData = getattr(cli, '_dataset')

    assert d is not None
    assert d.pan_id == b'\xab\xba'


def test_chan_handler(cli_factory) -> None:
    cli = cli_factory
    m = getattr(cli, '_handle_channel')
    m('Channel: 17', 'Channel:')
    d: ThreadNetworkData = getattr(cli, '_dataset')

    assert d is not None
    assert d.channel == 17


def test_nwk_key_handler(cli_factory) -> None:
    cli = cli_factory
    nwk_key = random.randbytes(16)
    m = getattr(cli, '_handle_nwk_key')
    m(f'Network Key: {nwk_key.hex().upper()}', 'Network Key:')
    d: ThreadNetworkData = getattr(cli, '_dataset')

    assert d is not None
    assert d.network_key == nwk_key


def test_nwk_name_handler(cli_factory) -> None:
    cli = cli_factory
    m = getattr(cli, '_handle_nwk_name')
    m('Network Name: Ferike001', 'Network Name:')
    d: ThreadNetworkData = getattr(cli, '_dataset')

    assert d is not None
    assert d.network_name == 'Ferike001'
