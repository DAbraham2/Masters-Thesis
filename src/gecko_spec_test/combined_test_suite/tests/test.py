from combined_test_suite.tests.utilities import address_in_scan
from gst_utils.logging import get_logger
from interface.ble import BleState
from scenario.mp import get_mp_scenario


def setUpRun():
    logger = get_logger(__name__)
    logger.info('started setup')
    get_mp_scenario().config()


def tearDownRun():
    logger = get_logger(__name__)
    get_mp_scenario().close()

    logger.info('finished testing')


dut_connection: int = -1
helper_connection: int = -1


class OtBle:
    def __init__(self):
        self.logger = get_logger(__name__)

    def v_child_adv(self):
        pass

    def v_child_cen(self):
        pass

    def v_child_peri(self):
        pass

    def v_child_scan(self):
        pass

    def v_child_stand(self):
        pass

    def v_detached_adv(self):
        pass

    def v_detached_cen(self):
        pass

    def v_detached_peri(self):
        pass

    def v_detached_scan(self):
        pass

    def v_detached_stand(self):
        pass

    def v_disabled_adv(self):
        pass

    def v_disabled_cen(self):
        pass

    def v_disabled_peri(self):
        pass

    def v_disabled_scan(self):
        pass

    def v_disabled_standby(self):
        pass

    def e_ble_adv(self):
        pass

    def e_ble_connect_dut(self):
        pass

    def e_ble_connect_helper(self):
        pass

    def e_ble_disconnect_dut(self):
        pass

    def e_ble_disconnect_helper(self):
        pass

    def e_ble_scan(self):
        pass

    def e_ble_stop_adv(self):
        pass

    def e_ble_stop_scan(self):
        pass

    def e_connect_helper(self):
        pass

    def e_ot_join(self):
        pass

    def e_ot_reset(self):
        pass

    def e_ot_restart(self):
        pass

    def e_ot_stop(self):
        pass


class ZigBle:
    def __init__(self):
        self.logger = get_logger(__name__)

    def v_diconnected_standby(self):
        pass

    def v_disconnected_advertising(self):
        pass

    def v_disconnected_central(self):
        pass

    def v_disconnected_peripheral(self):
        pass

    def v_disconnected_scanning(self):
        pass

    def v_joined_advertising(self):
        pass

    def v_joined_central(self):
        pass

    def v_joined_peripheral(self):
        pass

    def v_joined_scanning(self):
        pass

    def v_joined_standby(self):
        pass

    def v_tp_advertising(self):
        pass

    def v_tp_central(self):
        pass

    def v_tp_periperal(self):
        pass

    def v_tp_scanning(self):
        pass

    def v_tp_standby(self):
        pass

    def e_ble_adv(self):
        pass

    def e_ble_connect_to_dut(self):
        pass

    def e_ble_connect_to_helper(self):
        pass

    def e_ble_disconn_from_dut(self):
        pass

    def e_ble_disconn_from_helper(self):
        pass

    def e_ble_scan(self):
        pass

    def e_ble_stop_adv(self):
        pass

    def e_ble_stop_scan(self):
        pass

    def e_zb_analize(self):
        pass

    def e_zb_join(self):
        pass

    def e_zb_leave(self):
        pass

    def e_zb_tp(self):
        pass


class SingleZigbee:
    def __init__(self):
        self.logger = get_logger(__name__)

    def v_disconnected(self):
        pass

    def v_joined(self):
        pass

    def v_no_network(self):
        pass

    def v_throughputting(self):
        pass

    def v_with_ble_d(self):
        pass

    def v_with_ble_j(self):
        pass

    def v_with_ble_tp(self):
        pass

    def v_with_ot_d(self):
        pass

    def v_with_ot_j(self):
        pass

    def v_with_ot_tp(self):
        pass

    def e_add_ble(self):
        pass

    def e_add_ot(self):
        pass

    def e_analyze_data(self):
        pass

    def e_init_helper(self):
        pass

    def e_join(self):
        pass

    def e_leave(self):
        pass

    def e_reset(self):
        pass

    def e_start_data(self):
        pass


class SingleThread:
    def __init__(self):
        self.logger = get_logger(__name__)

    def v_thread_child(self):
        pass

    def v_thread_detached(self):
        pass

    def v_thread_disabled(self):
        pass

    def v_thread_leader(self):
        pass

    def v_with_ble_c(self):
        pass

    def v_with_ble_d(self):
        pass

    def v_with_zig_c(self):
        pass

    def v_with_zig_d(self):
        pass

    def e_add_ble(self):
        pass

    def e_add_zig(self):
        pass

    def e_factory_reset(self):
        pass

    def e_leader_stop(self):
        pass

    def e_thread_join(self):
        pass

    def e_thread_restart(self):
        pass

    def e_thread_stop(self):
        pass


class SingleProt:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dut = get_mp_scenario().dut
        self.ble_hello = False
        self.zig_state = None
        self.ot_state = ''

    def v_init(self):
        self.logger.info('Test started')

    def v_single_ble(self):
        assert self.ble_hello is True

    def v_single_thread(self):
        assert self.ot_state != ''

    def v_single_zig(self):
        assert self.zig_state.node_type is not None

    def e_factory_reset(self):
        self.dut.factory_reset()
        self.ble_hello = False

    def e_reset(self):
        self.dut.factory_reset()
        self.ble_hello = False

    def e_start_ble(self):
        self.dut.say_hello()
        self.ble_hello = True

    def e_start_th(self):
        self.ot_state = self.dut.get_thread_state()

    def e_start_zig(self):
        self.zig_state = self.dut.get_zig_state()


class SingleBle:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dut = get_mp_scenario().dut
        self.helper = get_mp_scenario().ble_helper

    def v_conn_initiate(self):
        self.logger.warning('Not implemented yet...')

    def v_advertising(self):
        assert self.dut.get_state() == BleState.ADVERTISING
        addr = self.dut.get_address()
        result = self.helper.expect_scan(addr, timeout=0.5)

        assert result is True

    def v_connection_as_central(self):
        self.logger.warning('Not implemented yet...')

    def v_connection_as_peripheral(self):
        assert self.dut.get_state() == BleState.CONNECTION
        assert helper_connection >= 0

    def v_controller_init(self):
        self.logger.debug('Whatever happens here...')

    def v_scanning(self):
        assert BleState.SCANNING == self.dut.get_state()
        addr = self.helper.get_address()
        found_helper = address_in_scan(addr, self.dut.scan_results())

        assert found_helper is True

    def v_standby(self):
        assert BleState.STANDBY == self.dut.get_state()

    def e_cancel(self):
        self.dut.stop_advertising()

    def e_connect_to_dut(self):
        addr = self.dut.get_address()
        self.helper.init_connection(addr)

    def e_connect_to_device(self):
        self.logger.warning('Not implemented yet...')

    def e_connect_to_helper(self):
        global helper_connection
        addr = self.dut.get_address()
        _, helper_connection = self.helper.init_connection(addr)

    def e_disconnect_from_dut(self):
        global helper_connection
        self.helper.disconnect(helper_connection)
        helper_connection = -1

    def e_disconnect_from_helper(self):
        self.logger.warning('Not implemented yet...')

    def e_init_ble_cli(self):
        self.dut.say_hello()

    def e_reset(self):
        self.dut.factory_reset()

    def e_start_advertising(self):
        self.dut.start_advertising()
        self.helper.start_scanning()

    def e_start_scan(self):
        self.helper.start_advertising()
        self.dut.start_scanning()

    def e_stop_scan(self):
        self.dut.stop_scanning()
        self.helper.stop_advertising()
