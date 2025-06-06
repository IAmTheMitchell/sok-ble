from __future__ import annotations

"""BLE device abstraction for SOK batteries."""

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional
import statistics

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
        self.temperature: float | None = None
        self.capacity: float | None = None
        self.num_cycles: int | None = None
        self.cell_voltages: list[float] | None = None
        # Derived metrics
        self.power: float | None = None
        self.cell_voltage_max: float | None = None
        self.cell_voltage_min: float | None = None
        self.cell_voltage_avg: float | None = None
        self.cell_voltage_median: float | None = None
        self.cell_voltage_delta: float | None = None
        self.cell_index_max: int | None = None
        self.cell_index_min: int | None = None

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
        """Poll the device for all telemetry and update attributes."""
        responses: dict[int, bytes] = {}
        async with self._connect() as client:
            await client.write_gatt_char(UUID_TX, _sok_command(0xC1))
            responses[0xCCF0] = bytes(await client.read_gatt_char(UUID_RX))

            await client.write_gatt_char(UUID_TX, _sok_command(0xC1))
            responses[0xCCF2] = bytes(await client.read_gatt_char(UUID_RX))

            await client.write_gatt_char(UUID_TX, _sok_command(0xC2))
            responses[0xCCF3] = bytes(await client.read_gatt_char(UUID_RX))

            await client.write_gatt_char(UUID_TX, _sok_command(0xC2))
            responses[0xCCF4] = bytes(await client.read_gatt_char(UUID_RX))

        parsed = SokParser.parse_all(responses)

        self.voltage = parsed["voltage"]
        self.current = parsed["current"]
        self.soc = parsed["soc"]
        self.temperature = parsed["temperature"]
        self.capacity = parsed["capacity"]
        self.num_cycles = parsed["num_cycles"]
        self.cell_voltages = parsed["cell_voltages"]

        # Derived metrics
        self.power = self.voltage * self.current
        self.cell_voltage_max = max(self.cell_voltages)
        self.cell_voltage_min = min(self.cell_voltages)
        self.cell_voltage_avg = sum(self.cell_voltages) / len(self.cell_voltages)
        self.cell_voltage_median = statistics.median(self.cell_voltages)
        self.cell_index_max = self.cell_voltages.index(self.cell_voltage_max)
        self.cell_index_min = self.cell_voltages.index(self.cell_voltage_min)
        self.cell_voltage_delta = (
            self.cell_voltage_max - self.cell_voltage_min
        )
