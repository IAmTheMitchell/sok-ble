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
        bytes.fromhex("ccf0000000102700000000000000320041000000"),
        bytes.fromhex("ccf2000000140000000000000000000000000000"),
        bytes.fromhex("ccf3000000003200000000000000000000000000"),
        bytes.fromhex("ccf401c50c0002c60c0003bf0c0004c00c000000"),
    ]

    dummy = DummyClient(responses)
    monkeypatch.setattr(device_mod, "establish_connection", None, raising=False)
    monkeypatch.setattr(device_mod, "BleakClientWithServiceCache", lambda *a, **k: dummy)

    dev = device_mod.SokBluetoothDevice(
        BLEDevice("00:11:22:33:44:55", "Test", None, -60)
    )

    await dev.async_update()

    assert dev.voltage == pytest.approx(13.066)
    assert dev.current == 10.0
    assert dev.soc == 65
    assert dev.temperature == 20.0
    assert dev.capacity == 100.0
    assert dev.num_cycles == 50
    assert dev.cell_voltages == [3.269, 3.27, 3.263, 3.264]
    assert dev.power == pytest.approx(130.66)
    assert dev.cell_voltage_max == 3.27
    assert dev.cell_voltage_min == 3.263
    assert dev.cell_voltage_avg == pytest.approx(3.2665)
    assert dev.cell_voltage_median == pytest.approx(3.2665)
    assert dev.cell_voltage_delta == pytest.approx(0.007)
    assert dev.cell_index_max == 1
    assert dev.cell_index_min == 2
