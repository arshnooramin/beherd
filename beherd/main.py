"""Home page, SOS button, and preset management."""

from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from beherd.alerts import send_alert
from beherd.extensions import db
from beherd.forms import PresetForm
from beherd.models import Contact, Preset, normalize_codeword
from beherd.phone import display

bp = Blueprint("main", __name__)


@bp.get("/")
def home():
    if not current_user.is_authenticated:
        return render_template("landing.html")
    return render_template("home.html", preset=current_user.preset)


@bp.post("/sos")
@login_required
def sos():
    preset = current_user.preset
    if preset is None:
        flash("Set up your preset before sending an alert.", "warning")
        return redirect(url_for("main.edit_preset"))

    result = send_alert(preset)
    flash(result.summary, "error" if result.failed else "success")
    return redirect(url_for("main.home"))


@bp.get("/preset")
@login_required
def view_preset():
    preset = current_user.preset
    if preset is None:
        return redirect(url_for("main.edit_preset"))
    return render_template("preset.html", preset=preset)


@bp.route("/preset/edit", methods=["GET", "POST"])
@login_required
def edit_preset():
    preset = current_user.preset
    data = None
    if preset is not None:
        region = current_app.config["DEFAULT_REGION"]
        data = {
            "name": preset.name,
            "codeword": preset.codeword,
            "message": preset.message,
            "contacts": [
                {"name": c.name or "", "phone": display(c.phone, region)}
                for c in preset.contacts
            ],
        }
    form = PresetForm(data=data, owner_phone=current_user.phone)

    if form.validate_on_submit():
        if preset is None:
            preset = Preset(user_id=current_user.id)
            db.session.add(preset)
        preset.name = form.name.data.strip()
        preset.codeword = normalize_codeword(form.codeword.data)
        preset.message = form.message.data.strip()
        preset.contacts = [
            Contact(position=i, name=name, phone=phone)
            for i, (name, phone) in enumerate(form.cleaned_contacts)
        ]
        db.session.commit()
        flash("Preset saved.", "success")
        return redirect(url_for("main.view_preset"))

    return render_template("preset_edit.html", form=form, is_new=preset is None)
