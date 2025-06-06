from sok_ble.const import minicrc, _sok_command


def test_minicrc_known_value():
    data = [0xEE, 0xC1, 0x00, 0x00, 0x00]
    assert minicrc(data) == 0xCE


def test_sok_command_crc_and_length():
    cmd = _sok_command(0xC1)
    assert len(cmd) == 6
    # CRC byte should match minicrc of base command frame
    assert cmd[-1] == minicrc([0xEE, 0xC1, 0x00, 0x00, 0x00])
