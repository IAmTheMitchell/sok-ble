from sok_ble.sok_parser import SokParser


def test_parse_info_basic():
    hex_data = bytes.fromhex("ccf0000000102700000000000000320041000000")
    result = SokParser.parse_info(hex_data)
    assert result == {
        "current": 10.0,
        "soc": 65,
        "num_cycles": 50,
    }


def test_parse_info_invalid_length():
    data = b"\x00" * 10
    try:
        SokParser.parse_info(data)
        assert False, "Expected InvalidResponseError"
    except Exception as err:
        from sok_ble.exceptions import InvalidResponseError

        assert isinstance(err, InvalidResponseError)
