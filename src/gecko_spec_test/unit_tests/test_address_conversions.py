from application.ble_applications import _bytes_from_address, _address_from_bytes


def test_ble_address_from_bytes():
    address = b'\x84\xfd\x27\x0e\x72\x47'

    result = _address_from_bytes(address)

    assert result == '84:fd:27:0e:72:47'


def test_bytes_from_address():
    address = '84:fd:27:0e:72:47'

    result = _bytes_from_address(address)

    assert result == b'\x84\xfd\x27\x0e\x72\x47'


def test_invariant_01():
    address = b'\x84\xfd\x27\x0e\x72\x47'

    result = _bytes_from_address(_address_from_bytes(address))

    assert result == address


def test_invariant_02():
    address = '84:fd:27:0e:72:47'

    result = _address_from_bytes(_bytes_from_address(address))

    assert result == address
