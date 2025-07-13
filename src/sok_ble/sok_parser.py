"""Parsing utilities for SOK BLE responses."""

from __future__ import annotations

import logging
import statistics
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
        """Parse the information frame for current, SOC and cycles."""
        logger.debug("parse_info input: %s", buf.hex())
        if len(buf) < 20:
            raise InvalidResponseError("Info buffer too short")

        current = get_le_int3(buf, 5) / 1000
        num_cycles = get_le_ushort(buf, 14)
        soc = get_le_ushort(buf, 16)

        result = {
            "current": current,
            "soc": soc,
            "num_cycles": num_cycles,
        }
        logger.debug("parse_info result: %s", result)
        return result

    @staticmethod
    def parse_temps(buf: bytes) -> float:
        """Parse the temperature from the temperature frame."""
        logger.debug("parse_temps input: %s", buf.hex())
        if len(buf) < 20:
            raise InvalidResponseError("Temp buffer too short")

        temperature = get_le_short(buf, 5)
        logger.debug("parse_temps result: %s", temperature)
        return temperature

    @staticmethod
    def parse_capacity_cycles(buf: bytes) -> Dict[str, float | int]:
        """Parse rated capacity."""
        logger.debug("parse_capacity_cycles input: %s", buf.hex())
        if len(buf) < 20:
            raise InvalidResponseError("Capacity buffer too short")

        capacity = get_be_uint3(buf, 5) / 128

        result = {"capacity": capacity}
        logger.debug("parse_capacity_cycles result: %s", result)
        return result

    @staticmethod
    def parse_cells(buf: bytes) -> list[float]:
        """Parse individual cell voltages."""
        logger.debug("parse_cells input: %s", buf.hex())
        if len(buf) < 20:
            raise InvalidResponseError("Cells buffer too short")

        cells = [0.0, 0.0, 0.0, 0.0]
        for x in range(4):
            cell_idx = buf[2 + x * 4]
            cells[cell_idx - 1] = get_le_ushort(buf, 3 + x * 4) / 1000
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

        voltage = statistics.mean(cells) * 4

        result = {
            "voltage": voltage,
            "current": info["current"],
            "soc": info["soc"],
            "temperature": temperature,
            "capacity": capacity_info["capacity"],
            "num_cycles": info["num_cycles"],
            "cell_voltages": cells,
        }
        logger.debug("parse_all result: %s", result)
        return result
