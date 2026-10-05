import os


def database_uri(uri: str) -> str:
    # Heroku-style "postgres://" URLs aren't accepted by SQLAlchemy.
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return uri


def settings_from_env() -> dict:
    env = os.environ
    return {
        "SECRET_KEY": env.get("SECRET_KEY"),
        "SQLALCHEMY_DATABASE_URI": database_uri(env.get("DATABASE_URL", "sqlite:///beherd.db")),
        # "twilio" sends real texts; "console" logs them instead, for local development.
        "MESSAGING_BACKEND": env.get("MESSAGING_BACKEND", "twilio"),
        "TWILIO_ACCOUNT_SID": env.get("TWILIO_ACCOUNT_SID"),
        "TWILIO_AUTH_TOKEN": env.get("TWILIO_AUTH_TOKEN"),
        "TWILIO_NUM": env.get("TWILIO_NUM"),
        "TWILIO_VERIFY_SID": env.get("TWILIO_VERIFY_SID"),
        # Region used to interpret phone numbers typed without a country code.
        "DEFAULT_REGION": env.get("DEFAULT_REGION", "US"),
    }
