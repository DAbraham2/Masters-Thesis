import time

from tenacity import retry, stop_after_attempt, retry_if_result, wait_random
from interface.ot import ThreadUtils
from interface.zigbee import ZigbeeUtils


class AddressNotFoundError(Exception):
    def __init__(self, address: bytes):
        super().__init__(f'Address not found: <<{address.hex(':')}>>')


def __is_false(value):
    return value is False


def __return_last_value(retry_state):
    return retry_state.outcome.result()


@retry(
    stop=stop_after_attempt(5),
    retry_error_callback=__return_last_value,
    retry=retry_if_result(__is_false),
)
def address_in_scan(address: bytes, scans: set[bytes]) -> bool:
    if address in scans:
        return True
    return False


@retry(
    stop=stop_after_attempt(5),
    retry_error_callback=__return_last_value,
    retry=retry_if_result(__is_false),
)
def is_state(expected: str, dut: ThreadUtils) -> bool:
    return dut.get_thread_state() == expected


@retry(
    stop=stop_after_attempt(5),
    retry_error_callback=__return_last_value,
    retry=retry_if_result(__is_false),
)
def is_child(dut: ThreadUtils) -> bool:
    return dut.get_thread_state() in ['child', 'router']


@retry(
    stop=stop_after_attempt(5),
    retry_error_callback=__return_last_value,
    retry=retry_if_result(__is_false),
    wait=wait_random(0.1, 0.8),
)
def compare_datasets(dut: ThreadUtils, helper: ThreadUtils) -> bool:
    d1 = dut.get_dataset()
    d2 = helper.get_dataset()

    return (
        d1.channel == d2.channel
        and d1.pan_id == d2.pan_id
        and d1.network_name == d2.network_name
    )


@retry(
    stop=stop_after_attempt(5),
    retry_error_callback=__return_last_value,
    retry=retry_if_result(__is_false),
    wait=wait_random(0.1, 0.8),
)
def compare_zig_states(dut: ZigbeeUtils, helper: ZigbeeUtils) -> bool:
    i1 = dut.get_zig_state()
    i2 = dut.get_zig_state()

    return i1.channel == i2.channel and i1.pan_id == i2.pan_id
