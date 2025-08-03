# SOK BLE

![Tests](https://github.com/IAmTheMitchell/sok-ble/actions/workflows/test.yml/badge.svg)
![Release](https://github.com/IAmTheMitchell/sok-ble/actions/workflows/release.yml/badge.svg)

Python library for interacting with SOK Bluetooth-enabled batteries.

## Quick Start

```python
import asyncio
from bleak import BleakScanner
from sok_ble.sok_bluetooth_device import SokBluetoothDevice


async def main() -> None:
    device = await BleakScanner.find_device_by_address("AA:BB:CC:DD:EE:FF")
    sok = SokBluetoothDevice(device)
    await sok.async_update()
    print("Voltage:", sok.voltage)


asyncio.run(main())
```

## References

[@zuccaro's comment](https://github.com/Louisvdw/dbus-serialbattery/issues/350#issuecomment-1500658941)
[Bluetooth-Devices/inkbird-ble](https://github.com/Bluetooth-Devices/inkbird-ble)
