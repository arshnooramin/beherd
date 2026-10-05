"""Sign-in with a phone number and a one-time code sent by text."""

import logging
from urllib.parse import urlsplit

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select

from beherd.extensions import db, login_manager
from beherd.forms import LoginForm, VerifyForm
from beherd.models import User

log = logging.getLogger(__name__)
bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))


def safe_next(target: str | None) -> str | None:
    """Only follow redirects back into this site."""
    if not target:
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or not target.startswith("/") or target.startswith("//"):
        return None
    return target


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        phone = form.phone.e164
        try:
            current_app.extensions["messenger"].start_verification(phone)
        except Exception:
            log.exception("Failed to start verification")
            flash("We couldn't text a code to that number. Check it and try again.", "error")
        else:
            session["pending_phone"] = phone
            return redirect(url_for("auth.verify", next=safe_next(request.args.get("next"))))
    return render_template("login.html", form=form)


@bp.route("/login/verify", methods=["GET", "POST"])
def verify():
    phone = session.get("pending_phone")
    if not phone:
        return redirect(url_for("auth.login"))

    form = VerifyForm()
    if form.validate_on_submit():
        if current_app.extensions["messenger"].check_verification(phone, form.code.data.strip()):
            session.pop("pending_phone")
            user = db.session.scalar(select(User).filter_by(phone=phone))
            if user is None:
                user = User(phone=phone)
                db.session.add(user)
                db.session.commit()
            login_user(user, remember=True)
            if next_url := safe_next(request.args.get("next")):
                return redirect(next_url)
            return redirect(url_for("main.home" if user.preset else "main.edit_preset"))
        form.code.errors.append("That code didn't work. Check it, or go back and send a new one.")
    return render_template("verify.html", form=form, phone=phone)


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been signed out.", "info")
    return redirect(url_for("main.home"))
