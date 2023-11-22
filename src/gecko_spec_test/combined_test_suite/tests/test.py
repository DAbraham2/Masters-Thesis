import random
import time
from combined_test_suite.tests.utilities import (
    address_in_scan,
    is_child,
    is_state,
    compare_datasets,
    compare_zig_states,
)
from gst_utils.gs_logging import get_logger
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
        self.dut = get_mp_scenario().dut
        self.ot = get_mp_scenario().ot_helper
        self.ble = get_mp_scenario().ble_helper

    def v_child_adv(self):
        assert is_child(self.dut) is True
        assert compare_datasets(self.dut, self.ot) is True
        addr = self.dut.get_address()
        assert self.ble.expect_scan(addr) is True

    def v_child_cen(self):
        assert is_child(self.dut) is True
        assert compare_datasets(self.dut, self.ot) is True
        assert dut_connection != -1

    def v_child_peri(self):
        assert is_child(self.dut) is True
        assert compare_datasets(self.dut, self.ot) is True
        assert helper_connection != -1

    def v_child_scan(self):
        assert is_child(self.dut) is True
        assert compare_datasets(self.dut, self.ot) is True
        addr = self.ble.get_address()
        assert address_in_scan(addr, self.dut.scan_results()) is True

    def v_child_stand(self):
        assert is_child(self.dut) is True
        assert compare_datasets(self.dut, self.ot) is True
        assert self.ble.get_state() == BleState.STANDBY

    def v_disabled_adv(self):
        assert is_state('disabled', self.dut)
        addr = self.dut.get_address()
        assert self.ble.expect_scan(addr) is True

    def v_disabled_cen(self):
        assert is_state('disabled', self.dut)
        assert dut_connection != -1

    def v_disabled_peri(self):
        assert is_state('disabled', self.dut)
        assert helper_connection != -1
        assert self.dut.get_state() == BleState.CONNECTION

    def v_disabled_scan(self):
        assert is_state('disabled', self.dut)
        addr = self.ble.get_address()
        assert address_in_scan(addr, self.dut.scan_results()) is True

    def v_disabled_standby(self):
        assert is_state('disabled', self.dut)
        assert self.dut.get_state() == BleState.STANDBY

    def e_ble_adv(self):
        self.dut.start_advertising()
        self.ble.start_scanning()

    def e_ble_connect_dut(self):
        """
        Helper connects to the dut
        :return:
        """
        global helper_connection
        addr = self.dut.get_address()
        for _ in range(8):
            try:
                _, helper_connection = self.ble.init_connection(addr)

                drop = self.ble.expect_drop(helper_connection, timeout=0.5)
                assert drop is False
                break
            except:
                continue

    def e_ble_connect_helper(self):
        """
        DUT connects to the helper
        :return:
        """
        self.logger.warning('Not implemented yet')
        global dut_connection
        dut_connection = 12

    def e_ble_disconnect_dut(self):
        self.logger.warning('Not implemented yet')
        global dut_connection
        dut_connection = -1

    def e_ble_disconnect_helper(self):
        global helper_connection
        assert self.ble.disconnect(helper_connection) is True

        helper_connection = -1

    def e_ble_scan(self):
        self.ble.start_advertising()
        self.dut.start_scanning()

    def e_ble_stop_adv(self):
        self.dut.stop_advertising()
        self.ble.stop_scanning()

    def e_ble_stop_scan(self):
        self.dut.stop_scanning()
        self.ble.stop_advertising()

    def e_ot_join(self):
        ds = self.ot.get_dataset()
        self.dut.join_network_with_nwk_key(ds.network_key)
        self.dut.get_dataset()

    def v_leader_cen(self):
        assert is_state('leader', self.dut)
        assert dut_connection != -1
        assert self.dut.get_state() == BleState.CONNECTION

    def e_factory_reset(self):
        self.dut.factory_reset()

    def v_leader_peri(self):
        assert is_state('leader', self.dut)
        assert self.dut.get_state() == BleState.CONNECTION

    def v_leader_standby(self):
        assert is_state('leader', self.dut)
        assert self.dut.get_state() == BleState.STANDBY

    def v_reset(self):
        self.logger.info('going to jail')
        self.ot.factory_reset()
        self.dut.factory_reset()

    def v_leader_scan(self):
        assert is_state('leader', self.dut)
        addr = self.ble.get_address()
        assert address_in_scan(addr, self.dut.scan_results()) is True

    def e_ot_leader_drop(self):
        self.ot.factory_reset()

    def v_leader_adv(self):
        assert is_state('leader', self.dut)
        addr = self.dut.get_address()
        assert self.ble.expect_scan(addr) is True


class ZigBle:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dut = get_mp_scenario().dut
        self.zig = get_mp_scenario().zig_helper
        self.ble = get_mp_scenario().ble_helper

    def v_diconnected_standby(self):
        assert self.dut.get_state() == BleState.STANDBY
        assert dut_connection == -1
        assert helper_connection == -1

    def v_disconnected_advertising(self):
        addr = self.dut.get_address()
        assert self.ble.expect_scan(addr) is True

    def v_disconnected_central(self):
        assert dut_connection != -1

    def v_disconnected_peripheral(self):
        assert helper_connection != -1
        assert self.dut.get_state() == BleState.STANDBY
        assert self.ble.expect_drop(helper_connection) is False

    def v_disconnected_scanning(self):
        addr = self.ble.get_address()
        assert address_in_scan(addr, self.dut.scan_results())

    def v_joined_advertising(self):
        assert compare_zig_states(self.dut, self.zig) is True
        addr = self.dut.get_address()
        assert self.ble.expect_scan(addr) is True

    def v_joined_central(self):
        assert compare_zig_states(self.dut, self.zig) is True
        assert dut_connection != -1

    def v_joined_peripheral(self):
        assert compare_zig_states(self.dut, self.zig) is True
        assert helper_connection != -1
        assert self.dut.get_state() == BleState.CONNECTION

    def v_joined_scanning(self):
        assert compare_zig_states(self.dut, self.zig) is True
        addr = self.ble.get_address()
        assert address_in_scan(addr, self.dut.scan_results())

    def v_joined_standby(self):
        assert compare_zig_states(self.dut, self.zig) is True
        assert self.dut.get_state() == BleState.STANDBY
        assert dut_connection == -1
        assert helper_connection == -1

    def v_tp_advertising(self):
        addr = self.dut.get_address()
        assert self.ble.expect_scan(addr) is True

    def v_tp_central(self):
        assert dut_connection != -1

    def v_tp_periperal(self):
        assert helper_connection != -1
        assert self.ble.expect_drop(helper_connection) is False

    def v_tp_scanning(self):
        addr = self.ble.get_address()
        assert address_in_scan(addr, self.dut.scan_results()) is True

    def v_tp_standby(self):
        assert dut_connection == -1
        assert helper_connection == -1
        assert self.ble.expect_scan(self.dut.get_address()) is False

    def e_ble_adv(self):
        self.dut.start_advertising()
        self.ble.start_scanning()

    def e_ble_connect_to_dut(self):
        global helper_connection
        addr = self.dut.get_address()
        for _ in range(8):
            try:
                _, helper_connection = self.ble.init_connection(addr)
                if self.ble.expect_drop(helper_connection, timeout=0.4) is False:
                    self.logger.info('conn opened')
                    break
            except:
                self.logger.warning('conn open issue..')
                continue

    def e_ble_connect_to_helper(self):
        self.logger.warning('Not implemented yet...')
        global dut_connection
        dut_connection = 12

    def e_ble_disconn_from_dut(self):
        global helper_connection
        if self.ble.disconnect(helper_connection):
            helper_connection = -1

    def e_ble_disconn_from_helper(self):
        global dut_connection
        dut_connection = -1

    def e_ble_scan(self):
        self.ble.start_advertising()
        self.dut.start_scanning()

    def e_ble_stop_adv(self):
        self.dut.stop_advertising()
        self.ble.stop_scanning()

    def e_ble_stop_scan(self):
        self.dut.stop_scanning()
        self.ble.stop_advertising()

    def e_zb_analize(self):
        self.logger.warning('not implemented yet..')

    def e_zb_join(self):
        info = self.zig.get_zig_state()
        self.dut.join_network(info.channel)

    def e_zb_leave(self):
        self.dut.leave_network()

    def e_zb_tp(self):
        self.logger.warning('not implemented yet..')


class SingleZigbee:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dut = get_mp_scenario().dut
        self.zig = get_mp_scenario().zig_helper
        self.ot = get_mp_scenario().ot_helper

    def v_disconnected(self):
        i1 = self.zig.get_zig_state()
        i2 = self.dut.get_zig_state()
        assert i1.network_state != 0x0
        assert i2.network_state == 0x0

    def v_joined(self):
        assert compare_zig_states(self.dut, self.zig) is True

    def v_no_network(self):
        i1 = self.zig.get_zig_state()
        i2 = self.dut.get_zig_state()

        assert i1.network_state == 0x0
        assert i2.network_state == 0x0

    def v_throughputting(self):
        self.logger.warning('Not implemented')

    def v_with_ble_d(self):
        self.logger.info('hopponálunk')

    def v_with_ble_j(self):
        self.logger.info('hopponálunk')

    def v_with_ble_tp(self):
        self.logger.info('hopponálunk')

    def v_with_ot_d(self):
        self.logger.info('hopponálunk')

    def v_with_ot_j(self):
        self.logger.info('hopponálunk')

    def v_with_ot_tp(self):
        self.logger.info('hopponálunk')

    def e_add_ble(self):
        self.logger.info('adding ble??')

    def e_add_ot(self):
        i1 = self.zig.get_zig_state()
        self.ot.create_network(channel=i1.channel, pan_id=i1.pan_id)

    def e_analyze_data(self):
        self.logger.warning('Not implemented...')

    def e_init_helper(self):
        channel = random.randint(11, 20)

        while True:
            pan_id = random.randbytes(2)
            if pan_id != b'\x00\x00' and pan_id != b'\xff\xff':
                break

        self.zig.create_network(channel, pan_id)

    def e_join(self):
        i1 = self.zig.get_zig_state()

        self.dut.join_network(i1.channel)

    def e_leave(self):
        self.dut.leave_network()

    def e_reset(self):
        self.dut.factory_reset()
        self.zig.reset()

    def e_start_data(self):
        self.logger.warning('Not implemented yet...')


# TODO
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

    def e_ot_ping_dut(self):
        ...

    def e_ot_ping_helper(self):
        ...

    def v_with_zig_ldr(self):
        ...

    def v_with_ble_ldr(self):
        ...


# TODO
class SingleProt:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dut = get_mp_scenario().dut
        self.ble_hello = False
        self.zig_state = None
        self.ot_state = ''

    def v_init(self):
        time.sleep(2)
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


# TODO
class ZigOtCmp:
    def __init__(self):
        self.dut = get_mp_scenario().dut
        self.ot = get_mp_scenario().ot_helper
        self.zig = get_mp_scenario().zig_helper

    def v_reset(self):
        ...

    def v_joined_child(self):
        ...

    def v_joined_ldr(self):
        ...

    def v_tp_child(self):
        ...

    def v_disc_child(self):
        ...

    def v_tp_ldr(self):
        ...

    def v_disc_ldr(self):
        ...

    def e_factory_reset(self):
        ...

    def e_zig_leave(self):
        ...

    def e_ot_leader_drop(self):
        ...

    def e_zig_tp_analize(self):
        ...

    def e_zig_join(self):
        ...

    def e_ot_ping_helper(self):
        ...

    def e_ot_ping_dut(self):
        ...

    def e_zig_tp_start(self):
        ...
