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
        ble_conn = bgapi.SocketConnector('127.0.0.1', port=4901)
        self.ble_helper = BleNcp(ble_conn, '')

        dut_conn = transport.transport_factory(
            'efr', '127.0.0.1', application_name='dut_sqa_dmp_cmp'
        )
        self.dut = DmpApplication(dut_conn)

        ot_conn = transport.transport_factory(
            'erf', '127.0.0.1', application_name='ot_ftd'
        )
        self.ot_helper = OtFtdSoc(ot_conn)

        zig_conn = transport.transport_factory(
            'erf', '127.0.0.1', application_name='z3_light'
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
