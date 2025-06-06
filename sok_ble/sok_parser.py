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

    @staticmethod
    def parse_temps(buf: bytes) -> float:
        """Parse the temperature from the temperature frame."""
        if len(buf) < 7:
            raise InvalidResponseError("Temp buffer too short")

        return get_le_short(buf, 5) / 10

    @staticmethod
    def parse_capacity_cycles(buf: bytes) -> Dict[str, float | int]:
        """Parse rated capacity and cycle count."""
        if len(buf) < 6:
            raise InvalidResponseError("Capacity buffer too short")

        capacity = get_le_ushort(buf, 0) / 100
        num_cycles = get_le_ushort(buf, 4)

        return {
            "capacity": capacity,
            "num_cycles": num_cycles,
        }

    @staticmethod
    def parse_cells(buf: bytes) -> list[float]:
        """Parse individual cell voltages."""
        if len(buf) < 8:
            raise InvalidResponseError("Cells buffer too short")

        return [
            get_le_ushort(buf, 0) / 1000,
            get_le_ushort(buf, 2) / 1000,
            get_le_ushort(buf, 4) / 1000,
            get_le_ushort(buf, 6) / 1000,
        ]

    @classmethod
    def parse_all(cls, responses: Dict[int, bytes]) -> Dict[str, float | int | list[float]]:
        """Parse all response buffers into a single dictionary."""
        required = {0xCCF0, 0xCCF2, 0xCCF3, 0xCCF4}
        if not required.issubset(responses):
            raise InvalidResponseError("Missing response buffers")

        info = cls.parse_info(responses[0xCCF0])
        temperature = cls.parse_temps(responses[0xCCF2])
        capacity_info = cls.parse_capacity_cycles(responses[0xCCF3])
        cells = cls.parse_cells(responses[0xCCF4])

        result = {
            **info,
            "temperature": temperature,
            **capacity_info,
            "cell_voltages": cells,
        }

        return result
