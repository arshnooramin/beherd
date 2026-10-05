import pytest

from beherd import create_app
from beherd.config import database_uri
from beherd.extensions import db


def test_heroku_postgres_url_is_rewritten():
    assert database_uri("postgres://u:p@h/db") == "postgresql://u:p@h/db"
    assert database_uri("sqlite:///x.db") == "sqlite:///x.db"


def test_twilio_backend_requires_credentials():
    with pytest.raises(RuntimeError, match="TWILIO_VERIFY_SID"):
        create_app(
            {
                "SECRET_KEY": "x",
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "MESSAGING_BACKEND": "twilio",
                "TWILIO_ACCOUNT_SID": "AC123",
                "TWILIO_AUTH_TOKEN": "t",
                "TWILIO_NUM": "+15705550199",
                "TWILIO_VERIFY_SID": None,
            }
        )


def test_csrf_protects_forms_but_not_the_webhook():
    app = create_app(
        {
            "SECRET_KEY": "x",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "MESSAGING_BACKEND": "console",
        }
    )
    client = app.test_client()
    assert client.post("/login", data={"phone": "5705550100"}).status_code == 400
    assert client.post("/sms", data={"From": "+15705550100", "Body": "hi"}).status_code == 200
    with app.app_context():
        db.engine.dispose()
