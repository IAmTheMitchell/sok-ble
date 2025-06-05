# 📋 SOK BLE Library – TODO Checklist

> Mark each task with `[x]` when complete.  
> Follow the milestones sequentially to keep commits small and tests passing.

---

## ⬜ M1 Repo Scaffold & Tooling
- [ ] **Create folder structure**
  - [ ] `sok_ble/`
  - [ ] `tests/`
- [ ] **Add empty/init files**
  - [ ] `sok_ble/__init__.py`
  - [ ] `README.md`
  - [ ] `pyproject.toml`
  - [ ] `requirements-dev.txt`
- [ ] **Configure tooling**
  - [ ] Add project metadata (`[project]`) to `pyproject.toml`
  - [ ] Add `ruff` and `mypy` sections (can be placeholders)
- [ ] **Populate `requirements-dev.txt`**
  - [ ] `bleak`
  - [ ] `pytest`
  - [ ] `pytest-asyncio`
  - [ ] `mypy`
  - [ ] `ruff`
- [ ] **Write initial GitHub Actions workflow** (`.github/workflows/ci.yml`)
  - [ ] Install uv
  - [ ] `uv pip install -r requirements-dev.txt`
  - [ ] `pytest`
- [ ] **Ensure `pytest` runs (0 tests, 0 failures)**

---

## ⬜ M2 Constants & CRC Utilities
- [ ] **Create `sok_ble/const.py`**
  - [ ] Add `UUID_RX`, `UUID_TX`
  - [ ] Define command byte lists (`CMD_NAME`, `CMD_INFO`, `CMD_DETAIL`, `CMD_SETTING`, `CMD_PROTECTION`, `CMD_BREAK`)
  - [ ] Implement `minicrc(data)` crc-8 function
  - [ ] Implement `_sok_command(cmd: int) -> bytes`
- [ ] **Add tests** `tests/test_const.py`
  - [ ] Validate `minicrc` result for sample data
  - [ ] Validate `_sok_command` length & crc byte
- [ ] **All tests green**

---

## ⬜ M3 Custom Exceptions
- [ ] **Create `sok_ble/exceptions.py`**
  - [ ] `class SokError`
  - [ ] `class BLEConnectionError(SokError)`
  - [ ] `class InvalidResponseError(SokError)`
- [ ] **Add tests** `tests/test_exceptions.py`
  - [ ] Check inheritance & raise behavior
- [ ] **All tests green**

---

## ⬜ M4 SokParser (Minimal)
- [ ] **Create `sok_ble/sok_parser.py`**
  - [ ] Copy endian helper functions (`get_le_short`, `get_le_ushort`, `get_le_int3`, `get_be_uint3`)
  - [ ] Implement `class SokParser` ➜ `parse_info(buf)` → returns `voltage`, `current`, `soc`
  - [ ] Raise `InvalidResponseError` on malformed buf
- [ ] **Add tests** `tests/test_parser_info.py`
  - [ ] Fixture hex → dict comparison
- [ ] **All tests green**

---

## ⬜ M5 SokParser (Full)
- [ ] **Extend parsing**
  - [ ] `parse_temps(buf)` → temperature °C
  - [ ] `parse_capacity_cycles(buf)` → capacity, num_cycles
  - [ ] `parse_cells(buf)` → list[float] volts
- [ ] **Implement `parse_all(responses)`** (aggregate full dict)
- [ ] **Add tests** `tests/test_parser_full.py`
  - [ ] Use fixtures for each buffer ID
  - [ ] Validate full sensor dict
- [ ] **All tests green**

---

## ⬜ M6 Device Skeleton
- [ ] **Create `sok_ble/sok_bluetooth_device.py`**
  - [ ] `__init__(ble_device, adapter=None)`
  - [ ] Async context `_connect()`
  - [ ] Implement minimal `async_update()` (info fetch only)
  - [ ] Store `voltage`, `current`, `soc`
- [ ] **Add tests** `tests/test_device_minimal.py`
  - [ ] Mock BleakClient read → info payload
  - [ ] Assert attributes populated
- [ ] **All tests green**

---

## ⬜ M7 Device Polling (Complete)
- [ ] **Expand `async_update()`**
  - [ ] Fetch 0xC1 (info, temps)
  - [ ] Fetch 0xC2 (capacity, cells) twice
  - [ ] Build `responses` dict → `SokParser.parse_all`
  - [ ] Update all attributes
- [ ] **Add tests** `tests/test_device_full.py`
  - [ ] Mock sequential reads with fixture payloads
  - [ ] Validate all attributes present
- [ ] **All tests green**

---

## ⬜ M8 Derived Metrics
- [ ] **Implement derived getters**
  - [ ] `power`
  - [ ] Cell stats: `cell_voltage_max`, `min`, `avg`, `median`, `delta`, `cell_index_max`, `cell_index_min`
  - [ ] `num_samples` counter
- [ ] **Add tests** `tests/test_derived.py`
  - [ ] Provide synthetic cell list, assert metrics
- [ ] **All tests green**

---

## ⬜ M9 Logging & Docs
- [ ] **Add `logging` calls**
  - [ ] DEBUG: command send/recv
  - [ ] INFO: update success
  - [ ] ERROR: exceptions
- [ ] **Enhance type hints across codebase**
- [ ] **Update `README.md`**
  - [ ] Quick usage snippet
  - [ ] Badge for CI
- [ ] **No test changes** (ensure existing pass)

---

## ⬜ M10 Integration (Mock)
- [ ] **Add `tests/test_integration_mock.py`**
  - [ ] Mock entire 4-message exchange
  - [ ] Call `async_update()` once
  - [ ] Ensure all public properties populated correctly
- [ ] **All tests green**

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