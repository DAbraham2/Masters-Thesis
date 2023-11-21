import time

from tenacity import retry, stop_after_attempt, retry_if_result


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
