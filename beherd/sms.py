"""Twilio webhook for incoming texts: a user texts their codeword to raise an alert."""

from flask import Blueprint, Response, abort, current_app, request, url_for
from sqlalchemy import select
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from beherd.alerts import send_alert
from beherd.extensions import db
from beherd.forms import normalize_phone
from beherd.models import User, normalize_codeword
from beherd.phone import InvalidPhoneNumber

bp = Blueprint("sms", __name__)


def signature_is_valid() -> bool:
    if not current_app.config["TWILIO_VALIDATE_SIGNATURE"]:
        return True
    validator = RequestValidator(current_app.config["TWILIO_AUTH_TOKEN"])
    return validator.validate(
        request.url, request.form, request.headers.get("X-Twilio-Signature", "")
    )


@bp.post("/sms")
def incoming():
    if not signature_is_valid():
        abort(403)

    try:
        sender = normalize_phone(request.form.get("From", ""))
    except InvalidPhoneNumber:
        sender = None
    user = db.session.scalar(select(User).filter_by(phone=sender)) if sender else None
    preset = user.preset if user else None

    resp = MessagingResponse()
    if preset is None:
        resp.message(
            "[BeHerd] This number doesn't have a BeHerd preset. "
            f"Set one up at {url_for('main.home', _external=True)}"
        )
    elif normalize_codeword(request.form.get("Body", "")) != preset.codeword:
        resp.message("[BeHerd] Codeword not recognized. No alert was sent.")
    else:
        resp.message(f"[BeHerd] {send_alert(preset).summary}")
    return Response(str(resp), mimetype="application/xml")
