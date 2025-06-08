import pytest
from sok_ble.sok_parser import SokParser


def test_parse_all():
    info_buf = bytes.fromhex(
        "ccf0000000102700000000000000320041000000"
    )
    temp_buf = bytes.fromhex(
        "ccf2000000fa0000000000000000000000000000"
    )
    cap_buf = bytes.fromhex(
        "ccf3000000003200000000000000000000000000"
    )
    cell_buf = bytes.fromhex(
        "ccf401c50c0002c60c0003bf0c0004c00c000000"
    )

    responses = {
        0xCCF0: info_buf,
        0xCCF2: temp_buf,
        0xCCF3: cap_buf,
        0xCCF4: cell_buf,
    }

    result = SokParser.parse_all(responses)
    assert result == {
        "voltage": pytest.approx(13.066, rel=1e-3),
        "current": 10.0,
        "soc": 65,
        "temperature": 25.0,
        "capacity": 100.0,
        "num_cycles": 50,
        "cell_voltages": [3.269, 3.27, 3.263, 3.264],
    }

