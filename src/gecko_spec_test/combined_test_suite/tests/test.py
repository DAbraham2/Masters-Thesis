from gst_utils.logging import get_logger
from scenario.mp import get_mp_scenario


def setUpRun():
    logger = get_logger(__name__)
    logger.info('started setup')
    get_mp_scenario().config()


def tearDownRun():
    logger = get_logger(__name__)
    get_mp_scenario().close()

    logger.info('finished testing')


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

    def v_init(self):
        pass

    def v_singleBle(self):
        pass

    def v_singleTh(self):
        pass

    def v_singleZig(self):
        pass

    def e_factory_reset(self):
        pass

    def e_reset(self):
        pass

    def e_start_ble(self):
        pass

    def e_start_th(self):
        pass

    def e_start_zig(self):
        pass


class SingleBle:
    def __init__(self):
        self.logger = get_logger(__name__)

    def v_Conn_Initiate(self):
        pass

    def v_advertising(self):
        pass

    def v_connection_as_central(self):
        pass

    def v_connection_as_peripheral(self):
        pass

    def v_controller_init(self):
        pass

    def v_scanning(self):
        pass

    def v_standby(self):
        pass

    def e_cancel(self):
        pass

    def e_connec_to_dut(self):
        pass

    def e_connect_to_device(self):
        pass

    def e_connect_to_helper(self):
        pass

    def e_disconnect_from_dut(self):
        pass

    def e_disconnect_from_helper(self):
        pass

    def e_init_ble_cli(self):
        pass

    def e_reset(self):
        pass

    def e_start_advertising(self):
        pass

    def e_start_scan(self):
        pass

    def e_stop_scan(self):
        pass
