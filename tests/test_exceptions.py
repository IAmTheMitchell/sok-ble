import pytest

from sok_ble.exceptions import BLEConnectionError, InvalidResponseError, SokError


def test_exception_inheritance():
    assert issubclass(BLEConnectionError, SokError)
    assert issubclass(InvalidResponseError, SokError)


def test_raises_ble_connection_error():
    with pytest.raises(BLEConnectionError):
        raise BLEConnectionError()


def test_raises_invalid_response_error():
    with pytest.raises(InvalidResponseError):
        raise InvalidResponseError()

