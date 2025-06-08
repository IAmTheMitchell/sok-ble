class SokError(Exception):
    """Base for SOK library errors."""


class BLEConnectionError(SokError):
    """Raised when BLE communication fails."""


class InvalidResponseError(SokError):
    """Raised when an invalid response is received."""

