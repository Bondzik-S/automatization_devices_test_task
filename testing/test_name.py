import pytest
from testing.scanner_handler import CheckQr

def fake_check_in_db_success(self, qr):
    """Simulates device found in the database (returns True)."""
    return True

def fake_check_in_db_failure(self, qr):
    """Simulates device not found in the database (returns None)."""
    return None

@pytest.mark.parametrize("qr, expected_color", [
    ("aqw", "Red"),
    ("12345", "Green"),
    ("qwertyu", "Fuzzy Wuzzy")
])
def test_check_len_color_valid(qr, expected_color):
    """
    Tests that check_len_color returns the correct color for valid QR codes.
    For lengths 3, 5, and 7, the expected colors are 'Red', 'Green', and 'Fuzzy Wuzzy', respectively.
    """
    checker = CheckQr()
    result = checker.check_len_color(qr)
    assert result == expected_color, f"Expected {expected_color} for QR '{qr}', got {result}"

@pytest.mark.parametrize("qr", [
    "qw",
    "qwer",
    "qwerty"
])
def test_check_len_color_invalid(qr):
    """
    Tests that check_len_color returns None for QR codes with invalid lengths.
    """
    checker = CheckQr()
    result = checker.check_len_color(qr)
    assert result is None, f"Expected None for QR '{qr}', got {result}"

def test_scan_check_out_list_not_in_db(monkeypatch):
    """
    Tests that when the device is not found in the database (check_in_db returns None),
    the second callback in scan_check_out_list returns ['Not in DB'].
    """
    qr = "qwe"
    checker = CheckQr()
    monkeypatch.setattr(CheckQr, "check_in_db", fake_check_in_db_failure)
    callbacks = checker.scan_check_out_list(qr)
    error_result = callbacks[1]()
    assert error_result == ['Not in DB'], f"Expected ['Not in DB'], got {error_result}"

def test_scan_check_out_list_invalid_length(monkeypatch):
    """
    Tests that for a QR code with an invalid length (e.g., 4 characters),
    the first callback in scan_check_out_list returns an error message about wrong QR length.
    """
    qr = "1234"
    checker = CheckQr()
    monkeypatch.setattr(CheckQr, "check_in_db", fake_check_in_db_success)
    callbacks = checker.scan_check_out_list(qr)
    error_result = callbacks[0]()
    assert isinstance(error_result, list), "Expected a list of errors"
    assert "Wrong qr length" in error_result[0], f"Expected error about wrong qr length, got {error_result[0]}"

def test_check_scanned_device_success(monkeypatch):
    """
    Tests that for a valid QR code (device found in the database and valid length),
    check_scanned_device calls can_add_device with the correct message.
    """
    qr = "abc"
    checker = CheckQr()
    monkeypatch.setattr(CheckQr, "check_in_db", fake_check_in_db_success)
    captured = {}
    def fake_can_add_device(self, message):
        captured["msg"] = message
        return message
    monkeypatch.setattr(CheckQr, "can_add_device", fake_can_add_device)
    checker.check_scanned_device(qr)
    expected_message = f"hallelujah {qr}"
    assert captured.get("msg") == expected_message, f"Expected '{expected_message}', got '{captured.get('msg')}'"

def test_check_scanned_device_failure(monkeypatch):
    """
    Tests that if a QR code is invalid (e.g., wrong length), check_scanned_device does not call can_add_device.
    """
    qr = "1234"
    checker = CheckQr()
    monkeypatch.setattr(CheckQr, "check_in_db", fake_check_in_db_success)
    captured = {}
    def fake_can_add_device(self, message):
        captured["msg"] = message
        return message
    monkeypatch.setattr(CheckQr, "can_add_device", fake_can_add_device)
    checker.check_scanned_device(qr)
    assert "msg" not in captured, "can_add_device should not be called if there is an error."

def test_static_methods():
    """
    Tests that the static methods send_error and can_add_device return the provided values.
    """
    assert CheckQr.send_error("Test error") == "Test error", "send_error should return the error message"
    assert CheckQr.can_add_device("Test device added") == "Test device added", "can_add_device should return the message"

if __name__ == '__main__':
    pytest.main()
