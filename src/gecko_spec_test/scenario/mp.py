import os
from typing import Optional

import bgapi

import transport
from application.ble_applications import BleNcp
from application.dmp_applications import DmpApplication
from application.ot_applications import OtFtdSoc
from application.zigbee_applications import ZigbeeSoc


class MpScenario:
    def __init__(self):
        self.zig_helper: Optional[ZigbeeSoc] = None
        self.ot_helper: Optional[OtFtdSoc] = None
        self.ble_helper: Optional[BleNcp] = None
        self.dut: Optional[DmpApplication] = None

    def config(self):
        ble_conn = bgapi.SocketConnector('10.150.64.19', port=4901)
        ble_api = os.path.join(os.path.dirname(__file__), 'sl_bt.xapi')
        self.ble_helper = BleNcp(ble_conn, ble_api)

        dut_conn = transport.transport_factory(
            'efr', '10.150.64.17', application_name='dut_sqa_dmp_cmp'
        )
        self.dut = DmpApplication(dut_conn)

        ot_conn = transport.transport_factory(
            'erf', '10.150.64.18', application_name='ot_ftd'
        )
        self.ot_helper = OtFtdSoc(ot_conn)

        zig_conn = transport.transport_factory(
            'erf', '10.150.64.14', application_name='z3_light'
        )
        self.zig_helper = ZigbeeSoc(zig_conn)

    def close(self):
        ...


_scenario: Optional[MpScenario] = None


def get_mp_scenario() -> MpScenario:
    global _scenario
    if _scenario is None:
        _scenario = MpScenario()

    return _scenario
