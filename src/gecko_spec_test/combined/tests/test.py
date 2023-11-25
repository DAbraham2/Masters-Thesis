from gst_utils.gs_logging import get_logger, log
from assertpy import assert_that

from interface.ble import BleState
from scenario.mp import get_mp_scenario
from gst_utils.test_utils import (
    zig_validate_state,
    address_in_scan,
    is_state,
    is_child,
    compare_datasets,
    compare_zig_states,
)
from transport._telnet_transport import ResponseNotFoundError

logger = get_logger('Combined')


@log(given_logger=logger)
def setUpRun():
    get_mp_scenario().config()


@log(given_logger=logger)
def tearDownRun():
    get_mp_scenario().dut.stop_scanning()
    get_mp_scenario().dut.stop_advertising()
    get_mp_scenario().dut.leave_network()
    get_mp_scenario().close()


class CombinedModel:
    def __init__(self):
        self._dut_ping_succ = 1
        self._dut_zig_succ = 1
        self._helper_ping_succ = 1
        self._helper_zig_succ = 1
        self.logger = get_logger('CombinedModel')
        self.dut = get_mp_scenario().dut
        self.ot = get_mp_scenario().ot_helper
        self.ble = get_mp_scenario().ble_helper
        self.zig = get_mp_scenario().zig_helper

        self.dut_ble_address = self.dut.get_address()
        self.helper_ble_address = self.ble.get_address()

        self.connection = -1
        self.dut_tp_drop: list[float] = []
        self.helper_tp_drop: list[float] = []

    @log
    def e_factory_reset(self):
        self.dut.factory_reset()
        if self.ble.expect_drop(self.connection):
            self.connection = -1

    @log
    def e_ble_connect(self):
        for i in range(8):
            _, self.connection = self.ble.init_connection(self.dut_ble_address)
            if self.ble.expect_drop(self.connection) is False:
                self.logger.warning('Connection failed on %s try', i)
                break
            self.connection = -1

    @log
    def v_advertise_child_joined(self):
        assert_that(self.ble.expect_scan(self.dut_ble_address)).is_true()

        assert_that(is_child(self.dut)).is_true()
        assert_that(compare_datasets(self.dut, self.ot))

        assert_that(zig_validate_state(self.dut, 0x2)).is_true()
        assert_that(compare_zig_states(self.dut, self.zig)).is_true()

        self.validate_connection_health()

    @log
    def e_ble_stop_scan(self):
        self.dut.stop_scanning()

    @log
    def e_ot_leave(self):
        self.dut.factory_reset()

    @log
    def v_peripheral_child_joined(self):
        assert_that(self.connection).is_not_equal_to(-1)

        assert_that(is_child(self.dut)).is_true()
        assert_that(compare_datasets(self.dut, self.ot))

        assert_that(zig_validate_state(self.dut, 0x2)).is_true()
        assert_that(compare_zig_states(self.dut, self.zig)).is_true()

        self.validate_connection_health()

    def e_ble_scan(self):
        self.ble.start_advertising()
        self.dut.start_scanning()

    @log
    def v_scan_disabled_joined(self):
        assert_that(address_in_scan(self.helper_ble_address, self.dut)).is_true()

        assert_that(is_child(self.dut)).is_false()

        assert_that(zig_validate_state(self.dut, 0x2)).is_true()
        assert_that(compare_zig_states(self.dut, self.zig)).is_true()

        self.validate_connection_health()

    @log
    def e_ot_join(self):
        d = self.ot.get_dataset()
        self.dut.join_network_with_nwk_key(d.network_key)

    @log
    def e_zig_tp_dut(self):
        i1 = self.zig.get_zig_state()
        drop = self.dut.start_throughput(i1.node_id)
        self._dut_zig_succ = self._dut_zig_succ * 0.9 + drop * 0.1

    @log
    def v_scan_child_joined(self):
        assert_that(address_in_scan(self.helper_ble_address, self.dut)).is_true()

        assert_that(is_child(self.dut)).is_true()
        assert_that(compare_datasets(self.dut, self.ot)).is_true()

        assert_that(zig_validate_state(self.dut, 0x2)).is_true()
        assert_that(compare_zig_states(self.dut, self.zig)).is_true()

        self.validate_connection_health()

    @log
    def v_standby_disabled_joined(self):
        assert_that(self.dut.get_state()).is_equal_to(BleState.STANDBY)
        assert_that(self.ble.expect_scan(self.dut_ble_address)).is_false()

        assert_that(is_child(self.dut)).is_false()

        assert_that(zig_validate_state(self.dut)).is_false()
        assert_that(compare_zig_states(self.dut, self.zig)).is_true()

        self.validate_connection_health()

    @log
    def v_scan_disabled_disconnected(self):
        assert_that(address_in_scan(self.helper_ble_address, self.dut)).is_true()
        assert_that(is_child(self.dut)).is_false()

        assert_that(zig_validate_state(self.dut)).is_true()

    @log
    def e_ble_stop_advertise(self):
        self.dut.stop_advertising()
        self.ble.clear_events()

    @log
    def e_init_helpers(self):
        self.ot.create_network()
        d = self.ot.get_dataset()

        self.zig.create_network(d.channel, d.pan_id)
        up = zig_validate_state(self.zig, 0x2)
        assert_that(up, 'Zig network must be created').is_true()
        self.ble.start_scanning()
        self.ble.start_advertising()

    def v_init(self):
        ...

    @log
    def e_ble_disconnect(self):
        self.ble.disconnect(self.connection)
        self.connection = -1

    @log
    def v_scan_child_disconnected(self):
        scan_res = address_in_scan(self.helper_ble_address, self.dut)
        assert_that(scan_res).is_true()

        assert_that(is_child(self.dut)).is_true()
        assert_that(compare_datasets(self.dut, self.ot)).is_true()

        assert_that(self.dut.get_zig_state().network_state).is_not_between(0x1, 0x5)

        self.validate_connection_health()

    @log
    def v_advertise_disabled_joined(self):
        res = self.ble.expect_scan(self.dut_ble_address)
        assert_that(res).is_true()

        assert_that(is_child(self.dut)).is_false()

        assert_that(zig_validate_state(self.dut, 0x2)).is_true()
        assert_that(compare_zig_states(self.dut, self.zig)).is_true()

        self.validate_connection_health()

    @log
    def v_peripheral_disabled_joined(self):
        assert_that(self.connection).is_not_equal_to(-1)
        assert_that(self.ble.expect_drop(self.connection)).is_false()

        assert_that(is_child(self.dut)).is_false()

        assert_that(zig_validate_state(self.dut, 0x2)).is_true()
        assert_that(compare_zig_states(self.dut, self.zig)).is_true()

        self.validate_connection_health()

    @log
    def v_peripheral_child_disconnected(self):
        assert_that(self.connection).is_not_equal_to(-1)
        assert_that(self.ble.expect_drop(self.connection)).is_false()

        assert_that(is_child(self.dut)).is_true()
        assert_that(compare_datasets(self.dut, self.ot)).is_true()

        assert_that(zig_validate_state(self.dut, 0x0)).is_true()

        self.validate_connection_health()

    @log
    def e_ot_ping_helper(self):
        addr = self.ot.get_ip_address()
        try:
            self.dut.ping(addr)
            self._dut_ping_succ = self._dut_ping_succ * 0.95 + 0.05
        except ResponseNotFoundError:
            self._dut_ping_succ = self._dut_ping_succ * 0.95

    @log
    def e_zig_join(self):
        i1 = self.zig.get_zig_state()
        self.dut.join_network(i1.channel)

    @log
    def v_standby_child_disconnected(self):
        scan_res = self.ble.expect_scan(self.dut_ble_address)
        assert_that(scan_res).is_false()

        assert_that(is_child(self.dut)).is_true()
        assert_that(compare_datasets(self.dut, self.ot)).is_true()

        assert_that(self.dut.get_zig_state().network_state).is_not_between(0x1, 0x5)

        self.validate_connection_health()

    @log
    def v_standby_child_joined(self):
        scan_res = self.ble.expect_scan(self.dut_ble_address)
        assert_that(scan_res).is_false()

        assert_that(is_child(self.dut)).is_true()
        assert_that(compare_datasets(self.dut, self.ot)).is_true()

        assert_that(self.dut.get_zig_state().network_state).is_between(0x2, 0x5)
        assert_that(compare_zig_states(self.dut, self.zig)).is_true()

        self.validate_connection_health()

    @log
    def e_zig_tp_helper(self):
        _id = self.dut.get_node_id()
        drop = self.zig.start_throughput(_id)
        self._helper_zig_succ = self._dut_zig_succ * 0.9 + drop * 0.1

    @log
    def v_advertise_child_disconnected(self):
        scan_res = self.ble.expect_scan(self.dut_ble_address)
        assert_that(scan_res).is_true()

        assert_that(self.dut.get_zig_state().network_state).is_not_between(0x1, 0x5)

        assert_that(is_child(self.dut)).is_true()
        assert_that(compare_datasets(self.dut, self.ot)).is_true()
        assert_that(self._dut_ping_succ).is_greater_than(0.89)

        self.validate_connection_health()

    @log
    def v_advertise_disabled_disconnected(self):
        scan_res = self.ble.expect_scan(self.dut_ble_address)
        assert_that(scan_res).is_true()

        assert_that(self.dut.get_zig_state().network_state).is_not_between(0x1, 0x5)
        assert_that(self.dut.get_thread_state()).is_in('disabled', 'detached')

    @log
    def e_ot_ping_dut(self):
        addr = self.dut.get_ip_address()
        try:
            self.ot.ping(addr)
        except ResponseNotFoundError:
            self._helper_ping_succ = self._dut_ping_succ * 0.95

    @log
    def e_ble_advertise(self):
        self.dut.start_advertising()

    @log
    def e_zig_leave(self):
        self.dut.leave_network()

    @log
    def v_global_start(self):
        ...

    @log
    def v_peripheral_disabled_disconnected(self):
        assert_that(self.connection).is_not_equal_to(-1)
        assert_that(self.ble.expect_drop(self.connection)).is_false()

        assert_that(self.dut.get_zig_state().network_state).is_not_between(0x1, 0x5)
        assert_that(self.dut.get_thread_state()).is_in('disabled', 'detached')

    @log
    def e_init(self):
        self.dut.factory_reset()
        self.dut.stop_advertising()
        self.dut.stop_scanning()
        self.zig.reset()
        self.ot.factory_reset()
        self.ble.reset()

    @log
    def v_standby_disabled_disconnected(self):
        scan_res = self.ble.expect_scan(self.dut_ble_address, timeout=5)
        assert_that(scan_res).is_false()

        assert_that(self.dut.get_state()).is_equal_to(BleState.STANDBY)
        assert_that(self.dut.get_zig_state().network_state).is_not_between(0x1, 0x5)
        assert_that(self.dut.get_thread_state()).is_not_in('child', 'router')

    def validate_connection_health(self):
        assert_that(self._dut_ping_succ).is_greater_than(0.89)
        assert_that(self._dut_zig_succ).is_greater_than(0.89)
        assert_that(self._helper_ping_succ).is_greater_than(0.89)
        assert_that(self._helper_zig_succ).is_greater_than(0.89)
