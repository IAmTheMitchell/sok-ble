"""Constants and helpers for interacting with SOK BLE batteries."""

from __future__ import annotations

UUID_RX = "0000ffe1-0000-1000-8000-00805f9b34fb"
UUID_TX = "0000ffe2-0000-1000-8000-00805f9b34fb"

# Command byte templates extracted from the reference addon
CMD_NAME = [0xEE, 0xC0, 0x00, 0x00, 0x00]
CMD_INFO = [0xEE, 0xC1, 0x00, 0x00, 0x00]
CMD_DETAIL = [0xEE, 0xC2, 0x00, 0x00, 0x00]
CMD_SETTING = [0xEE, 0xC3, 0x00, 0x00, 0x00]
CMD_PROTECTION = [0xEE, 0xC4, 0x00, 0x00, 0x00]
CMD_BREAK = [0xDD, 0xC0, 0x00, 0x00, 0x00]


def minicrc(data: list[int] | bytes) -> int:
    """Compute CRC-8 used by the SOK protocol."""

    crc = 0
    for byte in data:
        crc ^= byte & 0xFF
        for _ in range(8):
            crc = (crc >> 1) ^ 0x8C if (crc & 1) else crc >> 1
    return crc


def _sok_command(cmd: int) -> bytes:
    """Return a command frame with CRC for the given command byte."""

    data = [0xEE, cmd, 0x00, 0x00, 0x00]
    crc = minicrc(data)
    return bytes(data + [crc])
