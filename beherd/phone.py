import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat


class InvalidPhoneNumber(ValueError):
    pass


def normalize(raw: str, region: str) -> str:
    """Parse a user-entered phone number into E.164 (e.g. "+15705550100")."""
    try:
        parsed = phonenumbers.parse(raw, region)
    except NumberParseException as exc:
        raise InvalidPhoneNumber(raw) from exc
    if not phonenumbers.is_valid_number(parsed):
        raise InvalidPhoneNumber(raw)
    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)


def display(e164: str, region: str) -> str:
    """Format a stored number for people: national format at home, international abroad."""
    try:
        parsed = phonenumbers.parse(e164)
    except NumberParseException:
        return e164
    if phonenumbers.region_code_for_number(parsed) == region:
        return phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
    return phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
