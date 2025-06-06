from sok_ble.sok_parser import SokParser


def test_parse_info_basic():
    hex_data = bytes.fromhex(
        "E4 0C E9 0C EE 0C F3 0C 64 00 00 00 00 00 00 00 41 00"
    )
    result = SokParser.parse_info(hex_data)
    assert result == {
        "voltage": 13.23,
        "current": 10.0,
        "soc": 65,
    }


def test_parse_info_invalid_length():
    data = b"\x00" * 10
    try:
        SokParser.parse_info(data)
        assert False, "Expected InvalidResponseError"
    except Exception as err:
        from sok_ble.exceptions import InvalidResponseError

        assert isinstance(err, InvalidResponseError)
