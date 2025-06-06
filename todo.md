# 📋 SOK BLE Library – TODO Checklist

> Mark each task with `[x]` when complete.  
> Follow the milestones sequentially to keep commits small and tests passing.

---

## ⬜ M1 Repo Scaffold & Tooling
- [x] **Create folder structure**
  - [x] `sok_ble/`
  - [x] `tests/`
- [x] **Add empty/init files**
  - [x] `sok_ble/__init__.py`
  - [x] `README.md`
  - [x] `pyproject.toml`
  - [x] `requirements-dev.txt`
- [x] **Configure tooling**
  - [x] Add project metadata (`[project]`) to `pyproject.toml`
  - [x] Add `ruff` and `mypy` sections (can be placeholders)
- [x] **Populate `requirements-dev.txt`**
  - [x] `bleak`
  - [x] `pytest`
  - [x] `pytest-asyncio`
  - [x] `mypy`
  - [x] `ruff`
- [x] **Write initial GitHub Actions workflow** (`.github/workflows/ci.yml`)
  - [x] Install uv
  - [x] `uv pip install -r requirements-dev.txt`
  - [x] `pytest`
- [x] **Ensure `pytest` runs (0 tests, 0 failures)**

---

## ⬜ M2 Constants & CRC Utilities
- [x] **Create `sok_ble/const.py`**
  - [x] Add `UUID_RX`, `UUID_TX`
  - [x] Define command byte lists (`CMD_NAME`, `CMD_INFO`, `CMD_DETAIL`, `CMD_SETTING`, `CMD_PROTECTION`, `CMD_BREAK`)
  - [x] Implement `minicrc(data)` crc-8 function
  - [x] Implement `_sok_command(cmd: int) -> bytes`
- [x] **Add tests** `tests/test_const.py`
  - [x] Validate `minicrc` result for sample data
  - [x] Validate `_sok_command` length & crc byte
- [x] **All tests green**

---

## ⬜ M3 Custom Exceptions
- [x] **Create `sok_ble/exceptions.py`**
  - [x] `class SokError`
  - [x] `class BLEConnectionError(SokError)`
  - [x] `class InvalidResponseError(SokError)`
- [x] **Add tests** `tests/test_exceptions.py`
  - [x] Check inheritance & raise behavior
- [x] **All tests green**

---

## ⬜ M4 SokParser (Minimal)
- [x] **Create `sok_ble/sok_parser.py`**
  - [x] Copy endian helper functions (`get_le_short`, `get_le_ushort`, `get_le_int3`, `get_be_uint3`)
  - [x] Implement `class SokParser` ➜ `parse_info(buf)` → returns `voltage`, `current`, `soc`
  - [x] Raise `InvalidResponseError` on malformed buf
- [x] **Add tests** `tests/test_parser_info.py`
  - [x] Fixture hex → dict comparison
- [x] **All tests green**

---

## ⬜ M5 SokParser (Full)
- [x] **Extend parsing**
  - [x] `parse_temps(buf)` → temperature °C
  - [x] `parse_capacity_cycles(buf)` → capacity, num_cycles
  - [x] `parse_cells(buf)` → list[float] volts
- [x] **Implement `parse_all(responses)`** (aggregate full dict)
- [x] **Add tests** `tests/test_parser_full.py`
  - [x] Use fixtures for each buffer ID
  - [x] Validate full sensor dict
- [x] **All tests green**

---

## ⬜ M6 Device Skeleton
- [x] **Create `sok_ble/sok_bluetooth_device.py`**
  - [x] `__init__(ble_device, adapter=None)`
  - [x] Async context `_connect()`
  - [x] Implement minimal `async_update()` (info fetch only)
  - [x] Store `voltage`, `current`, `soc`
- [x] **Add tests** `tests/test_device_minimal.py`
  - [x] Mock BleakClient read → info payload
  - [x] Assert attributes populated
- [x] **All tests green**

---

## ⬜ M7 Device Polling (Complete)
- [x] **Expand `async_update()`**
  - [x] Fetch 0xC1 (info, temps)
  - [x] Fetch 0xC2 (capacity, cells) twice
  - [x] Build `responses` dict → `SokParser.parse_all`
  - [x] Update all attributes
- [x] **Add tests** `tests/test_device_full.py`
  - [x] Mock sequential reads with fixture payloads
  - [x] Validate all attributes present
- [x] **All tests green**

---

## ⬜ M8 Derived Metrics
- [x] **Implement derived getters**
  - [x] `power`
  - [x] Cell stats: `cell_voltage_max`, `min`, `avg`, `median`, `delta`, `cell_index_max`, `cell_index_min`
  - [x] `num_samples` counter
- [x] **Add tests** `tests/test_derived.py`
  - [x] Provide synthetic cell list, assert metrics
- [x] **All tests green**

---

## ⬜ M9 Logging & Docs
- [ ] **Add `logging` calls**
  - [x] DEBUG: command send/recv
  - [ ] INFO: update success
  - [ ] ERROR: exceptions
- [ ] **Enhance type hints across codebase**
- [ ] **Update `README.md`**
  - [x] Quick usage snippet
  - [x] Badge for CI
- [x] **No test changes** (ensure existing pass)

---

## ⬜ M10 Integration (Mock)
- [x] **Add `tests/test_integration_mock.py`**
  - [x] Mock entire 4-message exchange
  - [x] Call `async_update()` once
  - [x] Ensure all public properties populated correctly
- [x] **All tests green**

---

## ⬜ CI & Quality Gates
- [ ] Ruff lint passes (`ruff check .`)
- [ ] mypy type-check passes (`mypy sok_ble`)
- [ ] PyPI packaging check (`python -m build`, `twine check dist/*`)

---

## ⬜ Stretch Goals (Future)
- [ ] Notification support
- [ ] BLE scanning helper
- [ ] Write-command interface (protection toggle)
- [ ] Home Assistant `SensorUpdate` wrapper

---