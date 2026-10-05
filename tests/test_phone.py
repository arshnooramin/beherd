import pytest

from beherd.phone import InvalidPhoneNumber, display, normalize


@pytest.mark.parametrize(
    "raw",
    ["(570) 555-0100", "570-555-0100", "570.555.0100", "+1 570 555 0100", "15705550100"],
)
def test_normalize_us_formats(raw):
    assert normalize(raw, "US") == "+15705550100"


def test_normalize_international():
    assert normalize("+44 7911 123456", "US") == "+447911123456"


@pytest.mark.parametrize("raw", ["", "12345", "not a number", "+1 555 123 4567"])
def test_normalize_rejects_invalid(raw):
    with pytest.raises(InvalidPhoneNumber):
        normalize(raw, "US")


def test_display():
    assert display("+15705550100", "US") == "(570) 555-0100"
    assert display("+447911123456", "US") == "+44 7911 123456"
