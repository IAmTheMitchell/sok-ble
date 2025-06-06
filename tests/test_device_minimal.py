import pytest

from bleak.backends.device import BLEDevice

from sok_ble import sok_bluetooth_device as device_mod


class DummyClient:
    def __init__(self, *args, **kwargs):
        pass

    async def connect(self):
        return True

    async def disconnect(self):
        return True

    async def write_gatt_char(self, *args, **kwargs):
        return True

    async def read_gatt_char(self, *args, **kwargs):
        # Response bytes correspond to voltage=13.23V, current=10A, soc=65
        return bytes.fromhex(
            "E4 0C E9 0C EE 0C F3 0C 64 00 00 00 00 00 00 00 41 00"
        )


@pytest.mark.asyncio
async def test_minimal_update(monkeypatch):
    monkeypatch.setattr(device_mod, "establish_connection", None, raising=False)
    monkeypatch.setattr(device_mod, "BleakClientWithServiceCache", DummyClient)

    dev = device_mod.SokBluetoothDevice(
        BLEDevice("00:11:22:33:44:55", "Test", None, -60)
    )

    await dev.async_update()

    assert dev.voltage == 13.23
    assert dev.current == 10.0
    assert dev.soc == 65
