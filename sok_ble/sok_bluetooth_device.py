from __future__ import annotations

"""BLE device abstraction for SOK batteries."""

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from bleak.backends.device import BLEDevice

from sok_ble.const import UUID_RX, UUID_TX, _sok_command
from sok_ble.sok_parser import SokParser

try:
    from bleak_retry_connector import (
        BleakClientWithServiceCache,
        establish_connection,
    )
except Exception:  # pragma: no cover - optional dependency
    from bleak import BleakClient as BleakClientWithServiceCache
    establish_connection = None  # type: ignore[misc]


class SokBluetoothDevice:
    """Minimal BLE interface for a SOK battery."""

    def __init__(self, ble_device: BLEDevice, adapter: Optional[str] | None = None) -> None:
        self._ble_device = ble_device
        self._adapter = adapter

        self.voltage: float | None = None
        self.current: float | None = None
        self.soc: int | None = None

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[BleakClientWithServiceCache]:
        """Connect to the device and yield a BLE client."""
        if establish_connection:
            client = await establish_connection(
                BleakClientWithServiceCache,
                self._ble_device,
                self._ble_device.name or self._ble_device.address,
                adapter=self._adapter,
            )
        else:
            client = BleakClientWithServiceCache(
                self._ble_device,
                adapter=self._adapter,
            )
            await client.connect()
        try:
            yield client
        finally:
            await client.disconnect()

    async def async_update(self) -> None:
        """Fetch basic info from the battery and update state."""
        async with self._connect() as client:
            await client.write_gatt_char(UUID_TX, _sok_command(0xC1))
            data = await client.read_gatt_char(UUID_RX)
        info = SokParser.parse_info(bytes(data))
        self.voltage = info["voltage"]
        self.current = info["current"]
        self.soc = info["soc"]
