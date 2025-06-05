# 🚀 Project Blueprint – SOK BLE Library  
*(step-by-step plan → milestones → micro-steps → LLM prompts)*

---

## 0 🔄 Context
You already have a **spec** (see `<SPEC>` above) and reference code (`SokBt` addon).  
Goal: build a production-ready library **incrementally** with **test-driven development (TDD)**, managed by **uv** + **pytest**.

---

## 1 🗺️ High-Level Roadmap

| Milestone | Deliverable | Why |
|-----------|-------------|-----|
| **M1** | Repo scaffold + CI + dev tooling | foundation |
| **M2** | `const.py` with UUIDs, command helpers, CRC util | low-level primitives |
| **M3** | `exceptions.py` | typed error surface |
| **M4** | `SokParser` (minimal fields) + tests | parsing core |
| **M5** | `SokParser` (full fields) + tests | complete parsing |
| **M6** | `SokBluetoothDevice` skeleton (connect, async_update stub) + tests | I/O layer start |
| **M7** | `SokBluetoothDevice` full polling flow (mocked Bleak) + tests | complete device layer |
| **M8** | Derived metrics (cell stats, power) + tests | feature parity |
| **M9** | Logging, type hints, docs | polish |
| **M10**| End-to-end integration test (real or CI-mock harness) | confidence |

---

## 2 🔬 Milestones → Micro-Steps

### M1 Repo Scaffold
1. **Create folder layout** (`sok_ble/`, `tests/`, `pyproject.toml`, `requirements-dev.txt`).
2. **Add uv virtual-env instructions** in `README.md`.
3. **Configure ruff + mypy** defaults in `pyproject.toml`.
4. **CI (GitHub Actions)** workflow: `uv pip install -r requirements-dev.txt && pytest`.

### M2 Low-Level Constants & CRC
1. **Add `const.py`**  
   - UUID_RX, UUID_TX (`0000ffe1…`, `0000ffe2…`).  
   - Command byte templates (`CMD_NAME`, `CMD_INFO`, …).  
2. **Implement `minicrc()`** (crc-8 algorithm from addon).  
3. **_sok_command(cmd_id:int)->bytes** returns bytes + crc8.  
4. **Tests**: verify `minicrc([0xEE,0xC1,…]) == expected`, command length, crc matches captured frames.

### M3 Exceptions
1. Create `exceptions.py` with `class SokError(Exception)`, `BLEConnectionError`, `InvalidResponseError`.

### M4 SokParser (minimal)
1. Create `sok_parser.py` with `class SokParser: @staticmethod parse_info(buf:bytes)->dict`.
2. Implement parsing for **voltage, current, soc** using addon logic.
3. Unit tests with captured hex payload for `0xC1` (info).

### M5 SokParser (full)
1. Extend parses for temps (`0xC1/0xCCF2`), capacity, cycles, cell voltages (`0xC2/0xCCF4`).
2. Helpers for BE/LE int/short utilities (copied & unit-tested).
3. Unit tests covering outlier / corrupt frames (expect `InvalidResponseError`).

### M6 Device Skeleton
1. `sok_bluetooth_device.py` – constructor stores `BLEDevice`, sets attrs `None`.
2. Inject `BleakClient` via DI for testability.
3. `async_update()` – connect, write `_sok_command(0xC1)`, read response, call `SokParser` minimal, update attrs.
4. Tests: mock Bleak client, assert attrs populated.

### M7 Device Complete
1. Expand `async_update()` to sequentially fetch commands `0xC1`, `0xC2` (twice) mirroring addon flow.
2. Aggregate into attributes incl. derived metrics placeholders.
3. Tests: mock sequential reads with fixture payloads -> all attrs correct.

### M8 Derived Metrics
1. Implement `power`, `cell_voltage_*`, `num_samples` counter.
2. Tests for correctness with synthetic cell array.

### M9 Polish
1. Add `logging` statements (DEBUG, INFO, ERROR).
2. Add `@property` getters, type hints everywhere.
3. Update `README.md` usage snippet.

### M10 Integration Test
1. Write `tests/test_integration_mock.py` – uses fully mocked Bleak to simulate end-to-end update.
2. (Optional) real-hardware smoke test script excluded from CI.

---

## 3 📦 Chunk → Atomic Steps

We now slice each micro-step into **atomic steps** ≤ ~20 LOC changes so each commit can be TDD-driven.

Example (M2-Step 2):
- **2a**: add empty `minicrc()` raising `NotImplementedError`; write failing test.
- **2b**: implement algorithm; test passes.

Repeat this **red-green-refactor** pattern for every feature.

---

## 4 🤖 LLM Code-Gen Prompts

Each prompt below is **self-contained**, assumes prior code from previous prompt exists, and finishes with **tests passing**.  
Copy-paste into your code-gen LLM sequentially.

> **Notation**: replace `⟨...⟩` with actual content where needed.

---

### Prompt 1 `repo_scaffold`

```text
You are developing the SOK BLE Python library.

Task: create initial repo scaffold.

1. Create folders: sok_ble/, tests/.
2. Add empty files: sok_ble/__init__.py, pyproject.toml, requirements-dev.txt, README.md.
3. In pyproject.toml add minimal project metadata (`[project] name="sok-ble" ...`) and tool configs for ruff & mypy (can be blank placeholders).
4. In requirements-dev.txt list: bleak, pytest, pytest-asyncio, mypy, ruff.
5. Ensure all paths are created.

Write code for each file as needed. No application logic yet. Provide full file contents.
Finish when `pytest` (no tests yet) exits with code 0.
```

---

### Prompt 2 `const_module`

```text
Add `sok_ble/const.py`.

Requirements:
- Define UUID_RX = "0000ffe1-0000-1000-8000-00805f9b34fb"
- Define UUID_TX = "0000ffe2-0000-1000-8000-00805f9b34fb"
- Define command byte lists: CMD_NAME, CMD_INFO, CMD_DETAIL, CMD_SETTING, CMD_PROTECTION, CMD_BREAK (values from addon).
- Implement function `minicrc(data: list[int] | bytes) -> int` (crc8 algorithm from addon).
- Implement function `_sok_command(cmd: int) -> bytes` building `[0xEE, cmd, 0x00, 0x00, 0x00] + [crc]`.

Add tests in `tests/test_const.py`:
- Assert `minicrc([0xEE, 0xC1, 0, 0, 0]) == 0x??` (use value computed by addon).
- Assert `_sok_command(0xC1)[-1]` equals that crc.
Ensure tests pass.
```

---

### Prompt 3 `exceptions_module`

```text
Create `sok_ble/exceptions.py` with:

```python
class SokError(Exception): """Base for SOK library errors."""
class BLEConnectionError(SokError): ...
class InvalidResponseError(SokError): ...
```

No additional logic.  
Add tests in `tests/test_exceptions.py` to assert raising/issubclass relationships.
```

---

### Prompt 4 `parser_minimal`

```text
Create `sok_ble/sok_parser.py`.

Requirements:
- Utility functions: `get_le_short`, `get_le_ushort`, `get_le_int3`, `get_be_uint3` (copy from addon, include typing).
- `class SokParser`: staticmethod `parse_info(buf: bytes) -> dict[str, float|int]` which returns keys: "voltage", "current", "soc".
  - `voltage` = (mean of four cell placeholders *4)/1000. For now just placeholder: `struct.unpack('<H', buf[16:18])[0]` for soc; copy current logic.
- If buffer malformed (<18 bytes) raise `InvalidResponseError`.

Add tests in `tests/test_parser_info.py` feeding captured hex from addon to assert keys/values expected (you can hard-code expected numeric values).

All imports should reference `sok_ble.const` and `sok_ble.exceptions`.

Ensure tests pass.
```

---

### Prompt 5 `parser_full`

```text
Extend `sok_ble/sok_parser.py`.

1. Add `parse_temps(buf) -> float` returning °C (`get_le_short(buf, 5)/10`).
2. Add `parse_capacity_cycles(buf) -> dict` parsing rated Ah, num_cycles, etc.
3. Add `parse_cells(buf) -> list[float]` converting four cell mV -> V.

Expose `class SokParser` method `parse_all(responses: dict[int, bytes]) -> dict` that accepts a mapping:
{0xCCF0: info_buf, 0xCCF2: temp_buf, 0xCCF3: cap_buf, 0xCCF4: cell_buf}
and returns dictionary with all sensor keys per spec (voltage, current, soc, temp, capacity, num_cycles, cell_voltages).

Add new unit tests with fixture payloads for each buffer id, assert full dict.

Update existing tests to still pass.
```

---

### Prompt 6 `device_skeleton`

```text
Create `sok_ble/sok_bluetooth_device.py`.

Requirements:
- from bleak import BleakClient
- class SokBluetoothDevice
  - __init__(self, ble_device: BLEDevice, adapter: str | None = None)
  - async _connect() contextmanager returning BleakClient (use establish_connection if available, else plain BleakClient)
  - async_update(): writes `_sok_command(0xC1)` then waits for response via `client.read_gatt_char(UUID_RX)` (mock later), feeds to SokParser.parse_info, sets attrs.

Add tests `tests/test_device_minimal.py`:
- Patch BleakClient to return dummy response bytes.
- Instantiate device, await async_update(), assert attrs set correctly.

Use pytest-asyncio.
```

---

### Prompt 7 `device_full_poll`

```text
Expand `SokBluetoothDevice.async_update`.

Flow:
1. For each request/response pair:
   - 0xC1 -> expect 0xCCF0
   - 0xC1 -> expect 0xCCF2
   - 0xC2 -> expect 0xCCF3
   - 0xC2 -> expect 0xCCF4
2. Collect into dict and call `SokParser.parse_all`.
3. Map returned dict onto instance attributes & derived metrics (power, cell stats).

Update tests (`tests/test_device_full.py`) with mocked sequential reads returning payload fixtures; assert all attributes.

Ensure previous tests still pass.
```

---

### Prompt 8 `derived_metrics`

```text
Add helper methods to `SokBluetoothDevice`:

- @property power -> voltage * current
- Compute cell_voltage_max/min/avg/median/delta, indices.

Add tests `tests/test_derived.py` with synthetic cell array verifying metrics.
```

---

### Prompt 9 `logging_docs`

```text
Add logging statements at DEBUG in SokBluetoothDevice and SokParser.

Update README with quick-start example code snippet.

No new tests required. Ensure existing tests pass.
```

---

### Prompt 10 `integration_mock`

```text
Create tests/test_integration_mock.py.

- Use complete mocked BleakClient that simulates full 4-message exchange.
- Instantiate SokBluetoothDevice, call async_update(), assert all public getters.

All previous tests must still pass.
```

---

## 5 ✅ Right-Sizing Check
* Each prompt adds ≤ 2 files or ~150 LOC.  
* Every prompt ends with **tests passing**.  
* No orphan code; each new feature immediately integrated & covered.  
* Early prompts (1-4) validate core utilities before networking complexity.  
* BLE interaction mocked until final integration prompt, keeping CI stable.  
* Easy to roll back a single prompt if failing.

---

You can now feed **Prompt 1** to your code-generation LLM, run tests, then proceed sequentially.  
Happy coding! 🚀