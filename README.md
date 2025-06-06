# SOK BLE

![CI](https://github.com/IAmTheMitchell/sok-ble/actions/workflows/ci.yml/badge.svg)

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
