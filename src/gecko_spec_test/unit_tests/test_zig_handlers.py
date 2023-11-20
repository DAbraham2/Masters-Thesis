from plugins.cli.zigbeee import ZigbeeCore, ZigbeeStatus


def test_pan() -> None:
    pan_id = b'\xd4\x85'
    node = b'\x5d\x3a'
    actual = f'panID [0x{pan_id.hex().upper()}] nodeID [0x{node.hex().upper()}] xpan [0x(>)9D4BA0E1C4E24011]\r\n'
    expected = 'panID ['
    dut = ZigbeeCore()
    fn = getattr(dut, '_handle_pan_id')

    fn(actual, expected)

    status: ZigbeeStatus = getattr(dut, '_status')

    assert status.pan_id == pan_id
    assert status.node_id == node


def test_type() -> None:
    node = b'\x02'
    actual = f'nodeType [0x{node.hex().upper()}]\r\n'
    expected = 'nodeType ['
    dut = ZigbeeCore()
    fn = getattr(dut, '_handle_node_type')

    fn(actual, expected)

    status: ZigbeeStatus = getattr(dut, '_status')

    assert status.node_type == int.from_bytes(node)


def test_chan() -> None:
    chan = 2
    actual = f'node [(>)3425B4FFFEA94A68] chan [{chan}] pwr [3]\r\n'
    expected = 'chan ['
    dut = ZigbeeCore()
    fn = getattr(dut, '_handle_chan')

    fn(actual, expected)

    status: ZigbeeStatus = getattr(dut, '_status')

    assert status.channel == chan


def test_nwk() -> None:
    chan = 2
    actual = f'network state [0{chan}] Buffs: 75 / 75\r\n'
    expected = 'network state ['
    dut = ZigbeeCore()
    fn = getattr(dut, '_handle_nwk_state')

    fn(actual, expected)

    status: ZigbeeStatus = getattr(dut, '_status')

    assert status.network_state == chan
