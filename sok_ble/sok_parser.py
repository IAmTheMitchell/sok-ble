"""Parsing utilities for SOK BLE responses."""

from __future__ import annotations

import logging
import struct
from typing import Dict, Sequence

from sok_ble.exceptions import InvalidResponseError

logger = logging.getLogger(__name__)


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
        logger.debug("parse_info input: %s", buf.hex())
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

        result = {
            "voltage": voltage,
            "current": current,
            "soc": soc,
        }
        logger.debug("parse_info result: %s", result)
        return result

    @staticmethod
    def parse_temps(buf: bytes) -> float:
        """Parse the temperature from the temperature frame."""
        logger.debug("parse_temps input: %s", buf.hex())
        if len(buf) < 7:
            raise InvalidResponseError("Temp buffer too short")

        temperature = get_le_short(buf, 5) / 10
        logger.debug("parse_temps result: %s", temperature)
        return temperature

    @staticmethod
    def parse_capacity_cycles(buf: bytes) -> Dict[str, float | int]:
        """Parse rated capacity and cycle count."""
        logger.debug("parse_capacity_cycles input: %s", buf.hex())
        if len(buf) < 6:
            raise InvalidResponseError("Capacity buffer too short")

        capacity = get_le_ushort(buf, 0) / 100
        num_cycles = get_le_ushort(buf, 4)

        result = {
            "capacity": capacity,
            "num_cycles": num_cycles,
        }
        logger.debug("parse_capacity_cycles result: %s", result)
        return result

    @staticmethod
    def parse_cells(buf: bytes) -> list[float]:
        """Parse individual cell voltages."""
        logger.debug("parse_cells input: %s", buf.hex())
        if len(buf) < 8:
            raise InvalidResponseError("Cells buffer too short")

        cells = [
            get_le_ushort(buf, 0) / 1000,
            get_le_ushort(buf, 2) / 1000,
            get_le_ushort(buf, 4) / 1000,
            get_le_ushort(buf, 6) / 1000,
        ]
        logger.debug("parse_cells result: %s", cells)
        return cells

    @classmethod
    def parse_all(cls, responses: Dict[int, bytes]) -> Dict[str, float | int | list[float]]:
        """Parse all response buffers into a single dictionary."""
        logger.debug("parse_all input keys: %s", list(responses))
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
        logger.debug("parse_all result: %s", result)
        return result
