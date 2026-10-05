import logging
from dataclasses import dataclass, field

from flask import current_app

from beherd.models import Contact, Preset

log = logging.getLogger(__name__)


@dataclass
class AlertResult:
    sent: list[Contact] = field(default_factory=list)
    failed: list[Contact] = field(default_factory=list)

    @property
    def summary(self) -> str:
        total = len(self.sent) + len(self.failed)
        if not self.failed:
            if total == 1:
                return "Alert sent to your contact."
            return f"Alert sent to all {total} of your contacts."
        if not self.sent:
            return "Your alert couldn't be sent. If you're in danger, call emergency services."
        return f"Alert sent to {len(self.sent)} of {total} contacts. Some couldn't be reached."


def send_alert(preset: Preset) -> AlertResult:
    """Text every contact, carrying on past individual failures."""
    messenger = current_app.extensions["messenger"]
    result = AlertResult()
    for contact in preset.contacts:
        try:
            messenger.send_sms(contact.phone, preset.alert_body)
        except Exception:
            log.exception("Failed to alert contact %s for preset %s", contact.id, preset.id)
            result.failed.append(contact)
        else:
            result.sent.append(contact)
    return result
