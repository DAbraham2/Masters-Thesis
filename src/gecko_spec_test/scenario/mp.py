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
    for ip in ['10.150.64.19', '10.150.64.18', '10.150.64.17', '10.150.64.14']:
        with Telnet(ip, 4902) as conn:
            conn.write(b'sys reset sys\n')
            logger.info('reset device on: %s', ip)

    time.sleep(3)


class MpScenario:
    def __init__(self):
        self.logger = get_logger('gecko_spec.MpScenario')
        self.zig_helper: Optional[ZigbeeSoc] = None
        self.ot_helper: Optional[OtFtdSoc] = None
        self.ble_helper: Optional[BleNcp] = None
        self.dut: Optional[DmpApplication] = None

    def config(self):
        _reset_devices()

        ble_conn = bgapi.SocketConnector('10.150.64.19', port=4901)
        ble_api = os.path.join(os.path.dirname(__file__), 'sl_bt.xapi')
        self.ble_helper = BleNcp(ble_conn, ble_api)

        dut_conn = transport.transport_factory(
            'efr', '10.150.64.17', application_name='dut_sqa_dmp_cmp'
        )
        self.dut = DmpApplication(dut_conn)

        ot_conn = transport.transport_factory(
            'efr', '10.150.64.18', application_name='ot_ftd'
        )
        self.ot_helper = OtFtdSoc(ot_conn)

        zig_conn = transport.transport_factory(
            'efr', '10.150.64.14', application_name='z3_light'
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
