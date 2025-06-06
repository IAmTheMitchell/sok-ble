"""BLE device abstraction for SOK batteries."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional
import logging
import statistics

from bleak.backends.device import BLEDevice

from sok_ble.const import UUID_RX, UUID_TX, _sok_command
from sok_ble.sok_parser import SokParser

logger = logging.getLogger(__name__)

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

        # Housekeeping
        self.num_samples = 0

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[BleakClientWithServiceCache]:
        """Connect to the device and yield a BLE client."""
        logger.debug("Connecting to %s", self._ble_device.address)
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
            logger.debug("Disconnected from %s", self._ble_device.address)

    async def async_update(self) -> None:
        """Poll the device for all telemetry and update attributes."""
        responses: dict[int, bytes] = {}
        async with self._connect() as client:
            logger.debug("Send C1")
            await client.write_gatt_char(UUID_TX, _sok_command(0xC1))
            data = bytes(await client.read_gatt_char(UUID_RX))
            logger.debug("Recv 0xCCF0: %s", data.hex())
            responses[0xCCF0] = data

            logger.debug("Send C1")
            await client.write_gatt_char(UUID_TX, _sok_command(0xC1))
            data = bytes(await client.read_gatt_char(UUID_RX))
            logger.debug("Recv 0xCCF2: %s", data.hex())
            responses[0xCCF2] = data

            logger.debug("Send C2")
            await client.write_gatt_char(UUID_TX, _sok_command(0xC2))
            data = bytes(await client.read_gatt_char(UUID_RX))
            logger.debug("Recv 0xCCF3: %s", data.hex())
            responses[0xCCF3] = data

            logger.debug("Send C2")
            await client.write_gatt_char(UUID_TX, _sok_command(0xC2))
            data = bytes(await client.read_gatt_char(UUID_RX))
            logger.debug("Recv 0xCCF4: %s", data.hex())
            responses[0xCCF4] = data

        parsed = SokParser.parse_all(responses)
        logger.debug("Parsed update: %s", parsed)

        self.voltage = parsed["voltage"]
        self.current = parsed["current"]
        self.soc = parsed["soc"]
        self.temperature = parsed["temperature"]
        self.capacity = parsed["capacity"]
        self.num_cycles = parsed["num_cycles"]
        self.cell_voltages = parsed["cell_voltages"]

        self.num_samples += 1

    # Derived metrics -----------------------------------------------------

    @property
    def power(self) -> float | None:
        """Return instantaneous power in watts."""
        if self.voltage is None or self.current is None:
            return None
        return self.voltage * self.current

    @property
    def cell_voltage_max(self) -> float | None:
        cells = self.cell_voltages
        return max(cells) if cells else None

    @property
    def cell_voltage_min(self) -> float | None:
        cells = self.cell_voltages
        return min(cells) if cells else None

    @property
    def cell_voltage_avg(self) -> float | None:
        cells = self.cell_voltages
        if not cells:
            return None
        return sum(cells) / len(cells)

    @property
    def cell_voltage_median(self) -> float | None:
        cells = self.cell_voltages
        if not cells:
            return None
        return statistics.median(cells)

    @property
    def cell_voltage_delta(self) -> float | None:
        if self.cell_voltage_max is None or self.cell_voltage_min is None:
            return None
        return self.cell_voltage_max - self.cell_voltage_min

    @property
    def cell_index_max(self) -> int | None:
        cells = self.cell_voltages
        if not cells:
            return None
        return cells.index(max(cells))

    @property
    def cell_index_min(self) -> int | None:
        cells = self.cell_voltages
        if not cells:
            return None
        return cells.index(min(cells))
