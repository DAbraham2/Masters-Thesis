import os
import time
from telnetlib import Telnet
from typing import Optional

import bgapi

import transport
from application.ble_applications import BleNcp
from application.dmp_applications import DmpApplication
from application.ot_applications import OtFtdSoc
from application.zigbee_applications import ZigbeeSoc
from gst_utils.gs_logging import get_logger


logger = get_logger(__name__)


def _reset_devices() -> None:
    for ip in [_dut_ip, _zig_ip, _ble_ip, _ot_ip]:
        with Telnet(ip, 4902) as conn:
            conn.write(b'sys reset sys\n')
            logger.info('reset device on: %s', ip)
            time.sleep(2)
            try:
                conn.write(b'\n')
            except OSError:
                logger.info('connection closed successfully')

    time.sleep(5)


_dut_ip = '127.0.0.1'
_zig_ip = '127.0.0.1'
_ble_ip = '127.0.0.1'
_ot_ip = '127.0.0.1'


def add_configuration(dut_ip: str, ble_ip: str, zig_ip: str, ot_ip: str) -> None:
    global _dut_ip, _zig_ip, _ble_ip, _ot_ip
    logger.info('%s - %s - %s - %s', dut_ip, ble_ip, zig_ip, ot_ip)
    _dut_ip = dut_ip
    _ble_ip = ble_ip
    _zig_ip = zig_ip
    _ot_ip = ot_ip


class MpScenario:
    def __init__(self):
        self.logger = get_logger('gecko_spec.MpScenario')
        self.zig_helper: Optional[ZigbeeSoc] = None
        self.ot_helper: Optional[OtFtdSoc] = None
        self.ble_helper: Optional[BleNcp] = None
        self.dut: Optional[DmpApplication] = None

    def config(self):
        global _ble_ip, _dut_ip, _zig_ip, _ot_ip
        _reset_devices()

        ble_conn = bgapi.SocketConnector(_ble_ip, port=4901)
        ble_api = os.path.join(os.path.dirname(__file__), 'sl_bt.xapi')
        self.ble_helper = BleNcp(ble_conn, ble_api)

        dut_conn = transport.transport_factory(
            'efr', _dut_ip, application_name='dut_sqa_dmp_cmp'
        )
        self.dut = DmpApplication(dut_conn)

        ot_conn = transport.transport_factory('efr', _ot_ip, application_name='ot_ftd')
        self.ot_helper = OtFtdSoc(ot_conn)

        zig_conn = transport.transport_factory(
            'efr', _zig_ip, application_name='z3_light'
        )
        self.zig_helper = ZigbeeSoc(zig_conn)

    def close(self):
        del self.zig_helper
        del self.ot_helper
        del self.ble_helper
        del self.dut
        _reset_devices()


_scenario: Optional[MpScenario] = None


def get_mp_scenario() -> MpScenario:
    global _scenario
    if _scenario is None:
        _scenario = MpScenario()

    return _scenario
