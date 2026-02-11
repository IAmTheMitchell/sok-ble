import asyncio

import pytest
from bleak.backends.device import BLEDevice

from sok_ble import sok_bluetooth_device as device_mod
from sok_ble.exceptions import BLEConnectionError


class DummyClient:
    def __init__(self, *args, **kwargs):
        self._responses = [
            bytes.fromhex("ccf0000000102700000000000000320041000000"),
            bytes.fromhex("ccf2000000140000000000000000000000000000"),
            bytes.fromhex("ccf3000000003200000000000000000000000000"),
            bytes.fromhex("ccf401c50c0002c60c0003bf0c0004c00c000000"),
        ]

    async def connect(self):
        return True

    async def disconnect(self):
        return True

    async def write_gatt_char(self, *args, **kwargs):
        return True

    async def read_gatt_char(self, *args, **kwargs):
        return self._responses.pop(0)

    @property
    def services(self):
        return []


@pytest.mark.asyncio
async def test_minimal_update(monkeypatch):
    monkeypatch.setattr(device_mod, "establish_connection", None, raising=False)
    monkeypatch.setattr(device_mod, "BleakClientWithServiceCache", DummyClient)

    dev = device_mod.SokBluetoothDevice(BLEDevice("00:11:22:33:44:55", "Test", None))

    await dev.async_update()

    assert dev.voltage == pytest.approx(13.066)
    assert dev.current == 10.0
    assert dev.soc == 65


@pytest.mark.asyncio
async def test_disconnect_on_connect_failure(monkeypatch):
    class FailingClient:
        disconnect_calls = 0

        def __init__(self, *args, **kwargs):
            return None

        async def connect(self):
            return True

        async def disconnect(self):
            FailingClient.disconnect_calls += 1
            return True

        @property
        def services(self):
            raise asyncio.TimeoutError

    async def fast_sleep(*args, **kwargs):
        return None

    monkeypatch.setattr(device_mod, "establish_connection", None, raising=False)
    monkeypatch.setattr(device_mod, "BleakClientWithServiceCache", FailingClient)
    monkeypatch.setattr(device_mod.asyncio, "sleep", fast_sleep)

    dev = device_mod.SokBluetoothDevice(BLEDevice("00:11:22:33:44:55", "Test", None))

    with pytest.raises(BLEConnectionError):
        await dev.async_update()

    assert FailingClient.disconnect_calls == 3
