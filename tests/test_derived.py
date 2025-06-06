import pytest
from bleak.backends.device import BLEDevice

from sok_ble.sok_bluetooth_device import SokBluetoothDevice


def make_device():
    return SokBluetoothDevice(BLEDevice("00:11:22:33:44:55", "Test", None, -60))


def test_power_property():
    dev = make_device()
    dev.voltage = 12.5
    dev.current = -10.0
    assert dev.power == pytest.approx(-125.0)


def test_cell_voltage_stats():
    dev = make_device()
    dev.cell_voltages = [3.1, 3.15, 3.05, 3.2]

    assert dev.cell_voltage_max == 3.2
    assert dev.cell_voltage_min == 3.05
    assert dev.cell_voltage_avg == pytest.approx(3.125)
    assert dev.cell_voltage_median == pytest.approx(3.125)
    assert dev.cell_voltage_delta == pytest.approx(0.15)
    assert dev.cell_index_max == 3
    assert dev.cell_index_min == 2

