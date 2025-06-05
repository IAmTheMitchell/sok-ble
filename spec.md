# 🔧 SOK BLE Library Specification

## 📌 Purpose
A Python 3 library to interface with **SOK Bluetooth-enabled LiFePO₄ batteries**, allowing retrieval of telemetry data (voltage, current, SOC, cell voltages, cycles, temperature, etc.) via **polling** over BLE. Designed for use in **Home Assistant**, but modular enough for other Python environments.

---

## 📐 Architecture Overview

### Key Components

| Component               | Responsibility                                                   |
|------------------------|-------------------------------------------------------------------|
| `SokBluetoothDevice`   | Main class representing a single SOK battery. Manages BLE polling.|
| `SokParser`            | Parses raw bytes from BLE responses into structured sensor values.|
| `const.py`             | Holds UUIDs, Modbus command constants, and sensor keys.           |
| `models.py`            | (Optional) Data classes to encapsulate grouped sensor values.     |
| `exceptions.py`        | Custom exceptions for BLE connection and parsing errors.          |

---

## ✅ Design Decisions (Mirroring Inkbird Library)

| Decision                 | Implementation                                                                 |
|--------------------------|----------------------------------------------------------------------------------|
| Multiple devices          | Supported via one class instance per battery.                                  |
| Discovery                 | Not handled internally. User must supply a `BLEDevice`.                        |
| BLE library               | [`bleak`](https://github.com/hbldh/bleak) with `BleakClientWithServiceCache`. |
| Connection method         | `establish_connection` helper from `bluetooth_adapters`.                       |
| Data model                | State stored as attributes on the device instance.                             |
| Polling vs Notifications | **Polling only.**                                                               |
| Sensor access             | Standardized SI units (e.g., °C, V, A, Ah, kWh).                               |
| Update method             | Single `async_update()` to fetch all data.                                     |
| Parsing                   | Cleanly separated into `SokParser` for testability.                            |

---

## 🔧 Class Specification

### SokBluetoothDevice

```python
class SokBluetoothDevice:
    def __init__(self, ble_device: BLEDevice, adapter: Optional[str] = None): ...
    
    async def async_update(self) -> None: ...
    
    @property
    def voltage(self) -> float: ...
    @property
    def current(self) -> float: ...
    @property
    def soc(self) -> int: ...
    ...
```

- Accepts BLEDevice from bleak (must be discovered externally).
- async_update() handles:
    - Connection
    - Sending BLE command(s)
    - Awaiting response(s)
    - Parsing via SokParser
    - Updating internal attributes


## 🧮 Sensor List & Data Format

All values exposed in **standard SI units**:

| Name                                 | Type           | Units | Description                      |
|--------------------------------------|----------------|--------|----------------------------------|
| `voltage`                            | `float`        | V      | Total battery voltage            |
| `current`                            | `float`        | A      | Charge/discharge current         |
| `soc`                                | `int`          | %      | State of Charge                  |
| `temperature`                        | `float`        | °C     | Battery temperature              |
| `capacity`                           | `float`        | Ah     | Rated capacity                   |
| `power`                              | `float`        | W      | Derived: `voltage * current`     |
| `num_cycles`                         | `int`          | N      | Charge cycles                    |
| `cell_voltages`                      | `List[float]`  | V      | Individual cell voltages         |
| `cell_voltage_max/min/avg/median/delta` | `float`     | V      | Derived from `cell_voltages`     |
| `cell_index_max/min`                 | `int`          | —      | Index (0-based)                  |
| `total_charge_meter`                 | `float`        | Ah     | Cumulative charge                |
| `total_cycles_meter`                 | `float`        | N      | Historical count                 |
| `total_energy_charge_meter`         | `float`        | kWh    | Energy charged                   |
| `total_energy_discharge_meter`      | `float`        | kWh    | Energy discharged                |
| `total_energy_meter`                | `float`        | kWh    | Net energy total                 |
| `num_samples`                        | `int`          | N      | Internal debug count             |

---

## 🔐 BLE Characteristics & Command Strategy

- BLE UUIDs and command/register constants stored in `const.py`.
- Battery responses expected via a **modbus-like protocol**.
- BLE write used to send request, then read or response characteristic is parsed.
- Parsing must validate response length, register ID, and CRC/checksum (if present).

---

## ⚠️ Error Handling

| Scenario                     | Behavior                          |
|-----------------------------|-----------------------------------|
| BLE timeout / disconnection | Raise `BLEConnectionError`        |
| Bad response format or CRC  | Raise `InvalidResponseError`      |
| Partial failure             | Log warning, continue if safe     |
| Unexpected exception        | Raise upstream, no retry logic    |

All exceptions inherit from a shared base like `SokError`.

---

## 🧪 Testing Strategy

### 🧪 Framework & Tooling
- **Test framework**: [`pytest`](https://docs.pytest.org/)
- **Test runner**: `pytest`
- **Python env manager**: [`uv`](https://github.com/astral-sh/uv)
- All tests should be runnable with:
  ```bash
  uv pip install -r requirements-dev.txt
  pytest
  ```

### Test Types

| Type                  | Details                                                                  |
|-----------------------|--------------------------------------------------------------------------|
| **Parser unit tests** | Feed known raw byte responses into `SokParser`; validate output.         |
| **BLE simulation**    | Patch `BleakClient` using `pytest-mock`. Validate `async_update()` flow. |
| **Async tests**       | Use `pytest-asyncio` for coroutine-based logic.                          |
| **Regression tests**  | Add hex dumps from real batteries to guard against parser regressions.   |

---

## 🔍 Logging

- Use Python’s built-in `logging` module.
- Levels:
  - `DEBUG`: Raw BLE communication, parser input/output
  - `INFO`: Successful sensor update
  - `WARNING` / `ERROR`: Failed commands, parsing issues
- Do **not** set the global logging level — let the consumer configure it.

---

## 📦 Dependency Management (using `uv`)

1. Install `uv`:
   ```bash
   curl -Ls https://astral.sh/uv/install.sh | sh
   ```

2. Install all dev dependencies:
   ```bash
   uv pip install -r requirements-dev.txt
   ```

3. Example `requirements-dev.txt`:
   ```text
   bleak
   pytest
   pytest-asyncio
   mypy
   ruff
   ```

---

## 🧱 Folder Structure

```
sok_ble/
├── __init__.py
├── sok_bluetooth_device.py     # Handles BLE and state
├── sok_parser.py               # Raw byte parsing
├── const.py                    # UUIDs, commands, register IDs
├── models.py                   # (optional) Sensor dataclasses
├── exceptions.py               # Custom exceptions
tests/
├── test_parser.py
├── test_bluetooth_device.py
pyproject.toml                  # linting, formatting, type checking configs
requirements-dev.txt           # dev dependencies
```

---

## 🧭 Future Extensions (Not in Scope Yet)

- BLE notification support
- BLE scanning support
- Write commands to configure or toggle protection flags
- SensorUpdate-style abstraction for Home Assistant interface