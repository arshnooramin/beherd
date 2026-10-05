import pytest

from beherd import create_app
from beherd.extensions import db
from beherd.models import Contact, Preset, User

ME = "+15705550100"
FRIEND_1 = "+15705550101"
FRIEND_2 = "+15705550102"
FRIEND_3 = "+15705550103"
TWILIO_NUM = "+15705550199"


class FakeMessenger:
    def __init__(self):
        self.sent: list[tuple[str, str]] = []
        self.verifications: list[str] = []
        self.failing: set[str] = set()

    def send_sms(self, to, body):
        if to in self.failing:
            raise RuntimeError("delivery failed")
        self.sent.append((to, body))

    def start_verification(self, phone):
        self.verifications.append(phone)

    def check_verification(self, phone, code):
        return phone in self.verifications and code == "123456"


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "MESSAGING_BACKEND": "console",
            "TWILIO_NUM": TWILIO_NUM,
            "TWILIO_AUTH_TOKEN": "test-token",
            "TWILIO_VALIDATE_SIGNATURE": False,
            "WTF_CSRF_ENABLED": False,
            "DEFAULT_REGION": "US",
        }
    )
    app.extensions["messenger"] = FakeMessenger()
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def messenger(app) -> FakeMessenger:
    return app.extensions["messenger"]


def login(client, phone=ME):
    client.post("/login", data={"phone": phone})
    return client.post("/login/verify", data={"code": "123456"})


@pytest.fixture
def logged_in(client):
    login(client)
    return client


def make_preset(phone=ME, contacts=(FRIEND_1, FRIEND_2), codeword="pineapple"):
    user = db.session.query(User).filter_by(phone=phone).one_or_none() or User(phone=phone)
    user.preset = Preset(
        name="Alex",
        codeword=codeword,
        message="I need help",
        contacts=[Contact(position=i, phone=p) for i, p in enumerate(contacts)],
    )
    db.session.add(user)
    db.session.commit()
    return user.preset


def preset_form(**overrides):
    data = {
        "name": "Alex",
        "codeword": "Pineapple",
        "message": "I need help",
        "contacts-0-name": "Sam",
        "contacts-0-phone": "(570) 555-0101",
        "contacts-1-name": "",
        "contacts-1-phone": "570.555.0102",
    }
    data.update(overrides)
    return data
