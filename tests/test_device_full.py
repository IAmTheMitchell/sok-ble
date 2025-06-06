import pytest
from bleak.backends.device import BLEDevice

from sok_ble import sok_bluetooth_device as device_mod


class DummyClient:
    def __init__(self, responses):
        self._responses = list(responses)

    async def connect(self):
        return True

    async def disconnect(self):
        return True

    async def write_gatt_char(self, *args, **kwargs):
        return True

    async def read_gatt_char(self, *args, **kwargs):
        return self._responses.pop(0)


@pytest.mark.asyncio
async def test_full_update(monkeypatch):
    responses = [
        bytes.fromhex(
            "E4 0C E9 0C EE 0C F3 0C 64 00 00 00 00 00 00 00 41 00"
        ),
        bytes.fromhex("00 00 00 00 00 FA 00"),
        bytes.fromhex("10 27 00 00 32 00 00 00"),
        bytes.fromhex("E4 0C E9 0C EE 0C F3 0C"),
    ]

    dummy = DummyClient(responses)
    monkeypatch.setattr(device_mod, "establish_connection", None, raising=False)
    monkeypatch.setattr(device_mod, "BleakClientWithServiceCache", lambda *a, **k: dummy)

    dev = device_mod.SokBluetoothDevice(
        BLEDevice("00:11:22:33:44:55", "Test", None, -60)
    )

    await dev.async_update()

    assert dev.voltage == 13.23
    assert dev.current == 10.0
    assert dev.soc == 65
    assert dev.temperature == 25.0
    assert dev.capacity == 100.0
    assert dev.num_cycles == 50
    assert dev.cell_voltages == [3.3, 3.305, 3.31, 3.315]
    assert dev.power == pytest.approx(132.3)
    assert dev.cell_voltage_max == 3.315
    assert dev.cell_voltage_min == 3.3
    assert dev.cell_voltage_avg == pytest.approx(3.3075)
    assert dev.cell_voltage_median == pytest.approx(3.3075)
    assert dev.cell_voltage_delta == pytest.approx(0.015)
    assert dev.cell_index_max == 3
    assert dev.cell_index_min == 0
