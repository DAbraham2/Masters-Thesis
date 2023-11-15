from dataclasses import dataclass


@dataclass
class ThreadNetworkData:
    pan_id: bytes
    """16-bit unsigned integer that must be different from 0xFFFF"""

    network_key: bytes
    """16 bytes crypto-random number"""

    network_name: str
    """A human-readable name of the network in 16 byte length"""

    channel: int
    """15.4 channel number"""
