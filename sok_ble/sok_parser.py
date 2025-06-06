"""Parsing utilities for SOK BLE responses."""

from __future__ import annotations

import struct
from typing import Sequence, Dict

from sok_ble.exceptions import InvalidResponseError


# Endian helper functions copied from the reference addon

def get_le_short(data: Sequence[int] | bytes | bytearray, offset: int) -> int:
    """Read a little-endian signed short."""
    return struct.unpack_from('<h', bytes(data), offset)[0]


def get_le_ushort(data: Sequence[int] | bytes | bytearray, offset: int) -> int:
    """Read a little-endian unsigned short."""
    return struct.unpack_from('<H', bytes(data), offset)[0]


def get_le_int3(data: Sequence[int] | bytes | bytearray, offset: int) -> int:
    """Read a 3-byte little-endian signed integer."""
    b0, b1, b2 = bytes(data)[offset:offset + 3]
    val = b0 | (b1 << 8) | (b2 << 16)
    if val & 0x800000:
        val -= 0x1000000
    return val


def get_be_uint3(data: Sequence[int] | bytes | bytearray, offset: int) -> int:
    """Read a 3-byte big-endian unsigned integer."""
    b0, b1, b2 = bytes(data)[offset:offset + 3]
    return (b0 << 16) | (b1 << 8) | b2


class SokParser:
    """Parse buffers returned from SOK batteries."""

    @staticmethod
    def parse_info(buf: bytes) -> Dict[str, float | int]:
        """Parse the information frame for voltage, current and SOC."""
        if len(buf) < 18:
            raise InvalidResponseError("Info buffer too short")

        cells = [
            get_le_ushort(buf, 0),
            get_le_ushort(buf, 2),
            get_le_ushort(buf, 4),
            get_le_ushort(buf, 6),
        ]
        voltage = (sum(cells) / len(cells) * 4) / 1000

        current = get_le_int3(buf, 8) / 10

        soc = struct.unpack_from('<H', buf, 16)[0]

        return {
            "voltage": voltage,
            "current": current,
            "soc": soc,
        }
