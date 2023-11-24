import time

import bgapi.connector
from bgapi import BGLib
from bgapi.bglib import CommandFailedError
from tenacity import retry, stop_after_attempt, wait_exponential

from gst_utils.gs_logging import get_logger
from interface.ble import InitiatorBleDevice, MinimalBleDevice, BleUtils, BleState


def _address_from_bytes(original: bytes) -> str:
    """
    Turn bytes into bgapi compatible address.

    Specified format example: 84:fd:27:0e:72:47
    :param original: given address
    :return: bgapi address
    """
    return original.hex(':')


def _bytes_from_address(original: str) -> bytes:
    """
    Turns bgapi address into uniform bytes.

    :param original: given bgapi address `example: 84:fd:27:0e:72:47`
    :return: bytes address
    """
    spaced = original.replace(':', ' ').strip()
    return bytes.fromhex(spaced)


class BleNcp(InitiatorBleDevice, MinimalBleDevice, BleUtils):
    def __init__(self, connector: bgapi.connector.Connector, api):
        self.logger = get_logger('ble_ncp-cli')
        self._bgapi = BGLib(connector, api)
        self._state = BleState.STANDBY
        self._adv_handler = -1
        self._bgapi.open()

    def init_connection(self, address: bytes) -> tuple[bool, int]:
        self._state = BleState.INITIATING
        res, conn_handle = self._bgapi.bt.connection.open(
            _address_from_bytes(address),
            0x0,  # Address type
            0x1,  # Init phy
        )

        if res != 0:
            self._state = BleState.STANDBY
            return False, -1

        self._state = BleState.CONNECTION
        return True, conn_handle

    def disconnect(self, connection: int) -> bool:
        self._bgapi.bt.connection.close(connection)
        self._state = BleState.STANDBY
        return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(0.25, min=1, max=10))
    def start_scanning(self) -> bool:
        self.logger.debug('starting scan...')
        try:
            self._bgapi.bt.scanner.start(0x1, 0x2)
        except CommandFailedError as e:
            self.logger.critical('Error: %a', e)
            self.reset()
            raise
        self._state = BleState.SCANNING
        return True

    def stop_scanning(self) -> bool:
        self._bgapi.bt.scanner.stop()
        self._state = BleState.STANDBY
        return True

    def start_advertising(self) -> bool:
        _, self._adv_handler = self._bgapi.bt.advertiser.create_set()
        self.logger.debug('Advertiser set is: %s', self._adv_handler)
        _ = self._bgapi.bt.legacy_advertiser.start(self._adv_handler, 0x2)
        self._state = BleState.ADVERTISING
        time.sleep(0.3)
        return True

    def stop_advertising(self) -> bool:
        _ = self._bgapi.bt.advertiser.stop(self._adv_handler)
        _ = self._bgapi.bt.advertiser.delete_set(self._adv_handler)
        self._adv_handler = -1
        self._state = BleState.STANDBY
        return True

    def get_state(self) -> BleState:
        return self._state

    def get_address(self) -> bytes:
        _, addr, _ = self._bgapi.bt.system.get_identity_address()
        self.logger.debug(f'get_address-> {addr}')
        return _bytes_from_address(addr)

    def expect_scan(self, remote_address: bytes, *, timeout: float = 15) -> bool:
        address = _address_from_bytes(remote_address)
        for evt in self._bgapi.gen_events(timeout=None, max_time=timeout):
            s_evt = str(evt)
            if (
                'bt_evt_scanner_legacy_advertisement_report' in s_evt
                and address in s_evt
            ):
                return True

        return False

    def connection_opened(self, remote_address: bytes, *, timeout: float = 15) -> bool:
        address = _address_from_bytes(remote_address)
        for evt in self._bgapi.gen_events(None, max_time=timeout):
            s_evt = str(evt)
            if 'bt_evt_connection_opened' in s_evt and address in s_evt:
                return True

        return False

    def expect_drop(self, handle: int, *, timeout: float = 5) -> bool:
        for evt in self._bgapi.gen_events(None, max_time=timeout):
            s_evt = str(evt)
            if 'bt_evt_connection_closed' in s_evt and f'connection={handle}' in s_evt:
                return True

        return False

    def reset(self):
        self.logger.debug('resetting...')
        self._bgapi.bt.system.reset(0)
        time.sleep(2)
