from sok_ble.sok_parser import SokParser


def test_parse_all():
    info_buf = bytes.fromhex(
        "E4 0C E9 0C EE 0C F3 0C 64 00 00 00 00 00 00 00 41 00"
    )
    temp_buf = bytes.fromhex(
        "00 00 00 00 00 FA 00"
    )
    cap_buf = bytes.fromhex(
        "10 27 00 00 32 00 00 00"
    )
    cell_buf = bytes.fromhex(
        "E4 0C E9 0C EE 0C F3 0C"
    )

    responses = {
        0xCCF0: info_buf,
        0xCCF2: temp_buf,
        0xCCF3: cap_buf,
        0xCCF4: cell_buf,
    }

    result = SokParser.parse_all(responses)
    assert result == {
        "voltage": 13.23,
        "current": 10.0,
        "soc": 65,
        "temperature": 25.0,
        "capacity": 100.0,
        "num_cycles": 50,
        "cell_voltages": [3.3, 3.305, 3.31, 3.315],
    }

