"""Sending texts and phone verification codes."""

import logging
import secrets
from typing import Protocol

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

log = logging.getLogger(__name__)


class Messenger(Protocol):
    def send_sms(self, to: str, body: str) -> None: ...

    def start_verification(self, phone: str) -> None: ...

    def check_verification(self, phone: str, code: str) -> bool: ...


class TwilioMessenger:
    def __init__(self, account_sid: str, auth_token: str, from_number: str, verify_sid: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
        self.verify = self.client.verify.v2.services(verify_sid)

    def send_sms(self, to: str, body: str) -> None:
        self.client.messages.create(to=to, from_=self.from_number, body=body)

    def start_verification(self, phone: str) -> None:
        self.verify.verifications.create(to=phone, channel="sms")

    def check_verification(self, phone: str, code: str) -> bool:
        try:
            check = self.verify.verification_checks.create(to=phone, code=code)
        except TwilioRestException as exc:
            # 404 means the code expired, was already used, or ran out of attempts.
            if exc.status == 404:
                return False
            raise
        return check.status == "approved"


class ConsoleMessenger:
    """Local development: logs texts and verification codes instead of sending them."""

    def __init__(self) -> None:
        self.codes: dict[str, str] = {}

    def send_sms(self, to: str, body: str) -> None:
        log.warning("[console SMS] to %s: %s", to, body)

    def start_verification(self, phone: str) -> None:
        code = f"{secrets.randbelow(10**6):06d}"
        self.codes[phone] = code
        log.warning("[console SMS] verification code for %s: %s", phone, code)

    def check_verification(self, phone: str, code: str) -> bool:
        expected = self.codes.get(phone)
        if expected is None or not secrets.compare_digest(expected, code):
            return False
        del self.codes[phone]
        return True


def create_messenger(config) -> Messenger:
    backend = config["MESSAGING_BACKEND"]
    if backend == "console":
        return ConsoleMessenger()
    if backend == "twilio":
        required = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_NUM", "TWILIO_VERIFY_SID"]
        if missing := [key for key in required if not config.get(key)]:
            raise RuntimeError(
                f"Missing settings for MESSAGING_BACKEND=twilio: {', '.join(missing)}. "
                "Set them, or use MESSAGING_BACKEND=console for local development."
            )
        return TwilioMessenger(
            config["TWILIO_ACCOUNT_SID"],
            config["TWILIO_AUTH_TOKEN"],
            config["TWILIO_NUM"],
            config["TWILIO_VERIFY_SID"],
        )
    raise RuntimeError(f"Unknown MESSAGING_BACKEND {backend!r}; use 'twilio' or 'console'.")
