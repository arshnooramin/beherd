from flask import current_app
from flask_wtf import FlaskForm
from wtforms import (
    FieldList,
    Form,
    FormField,
    StringField,
    SubmitField,
    TelField,
    TextAreaField,
    ValidationError,
)
from wtforms.validators import DataRequired, Length, Regexp

from beherd.models import MAX_CONTACTS, MIN_CONTACTS, normalize_codeword
from beherd.phone import InvalidPhoneNumber, normalize

# Twilio intercepts these words for opt-out/help handling, so they never reach the app.
RESERVED_KEYWORDS = {
    "cancel", "end", "help", "info", "quit", "start", "stop", "stopall",
    "unstop", "unsubscribe", "yes",
}


def normalize_phone(raw: str) -> str:
    return normalize(raw, current_app.config["DEFAULT_REGION"])


class LoginForm(FlaskForm):
    phone = TelField("Phone number", validators=[DataRequired(), Length(max=30)])
    submit = SubmitField("Text me a code")

    def validate_phone(self, field):
        try:
            field.e164 = normalize_phone(field.data)
        except InvalidPhoneNumber:
            raise ValidationError("Enter a valid phone number, including the area code.")


class VerifyForm(FlaskForm):
    code = StringField(
        "Verification code",
        validators=[DataRequired(), Regexp(r"^\s*\d{4,10}\s*$", message="Enter the digits from the text.")],
    )
    submit = SubmitField("Sign in")


class ContactForm(Form):
    name = StringField("Name", validators=[Length(max=100)])
    phone = TelField("Phone", validators=[Length(max=30)])

    @property
    def is_blank(self) -> bool:
        return not (self.name.data or "").strip() and not (self.phone.data or "").strip()


class PresetForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    codeword = StringField("Codeword", validators=[DataRequired(), Length(max=50)])
    message = TextAreaField("Alert text", validators=[DataRequired(), Length(max=500)])
    # Always MAX_CONTACTS rows; blank rows are ignored.
    contacts = FieldList(FormField(ContactForm), min_entries=MAX_CONTACTS, max_entries=MAX_CONTACTS)
    submit = SubmitField("Save preset")

    def __init__(self, *args, owner_phone: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner_phone = owner_phone
        self.contacts_error: str | None = None
        self.cleaned_contacts: list[tuple[str | None, str]] = []

    def validate_codeword(self, field):
        if normalize_codeword(field.data) in RESERVED_KEYWORDS:
            raise ValidationError("That word is reserved by the texting service. Pick another.")

    def validate(self, extra_validators=None) -> bool:
        valid = super().validate(extra_validators)

        seen = set()
        for entry in self.contacts:
            row = entry.form
            if row.is_blank:
                continue
            name = (row.name.data or "").strip() or None
            raw_phone = (row.phone.data or "").strip()
            if not raw_phone:
                row.phone.errors.append("Add a phone number for this contact.")
                valid = False
                continue
            try:
                phone = normalize_phone(raw_phone)
            except InvalidPhoneNumber:
                row.phone.errors.append("Enter a valid phone number, including the area code.")
                valid = False
                continue
            if phone == self.owner_phone:
                row.phone.errors.append("That's your own number. Add someone else.")
                valid = False
            elif phone in seen:
                row.phone.errors.append("This number is already on the list.")
                valid = False
            seen.add(phone)
            self.cleaned_contacts.append((name, phone))

        filled = sum(not entry.form.is_blank for entry in self.contacts)
        if filled < MIN_CONTACTS:
            self.contacts_error = (
                "Add an emergency contact."
                if MIN_CONTACTS == 1
                else f"Add at least {MIN_CONTACTS} emergency contacts."
            )
            valid = False
        return valid
