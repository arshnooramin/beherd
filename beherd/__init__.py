"""BeHerd: campus safety app that texts your emergency contacts."""

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from beherd import auth, main, sms
from beherd.config import settings_from_env
from beherd.extensions import csrf, db, login_manager
from beherd.messaging import create_messenger
from beherd.models import MAX_CONTACTS, MIN_CONTACTS
from beherd.phone import display


def create_app(overrides: dict | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.from_mapping(settings_from_env())
    app.config.update(overrides or {})
    app.config.setdefault("TWILIO_VALIDATE_SIGNATURE", app.config["MESSAGING_BACKEND"] == "twilio")
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY is not set.")

    # Hosts like PythonAnywhere terminate HTTPS at a proxy; Twilio signatures
    # are computed over the public https:// URL.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    app.extensions["messenger"] = create_messenger(app.config)

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(sms.bp)
    csrf.exempt(sms.bp)

    app.add_template_filter(lambda e164: display(e164, app.config["DEFAULT_REGION"]), "phone")
    app.context_processor(lambda: {"min_contacts": MIN_CONTACTS, "max_contacts": MAX_CONTACTS})

    with app.app_context():
        db.create_all()

    return app
