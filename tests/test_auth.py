from beherd.extensions import db
from beherd.models import User
from tests.conftest import ME, login


def test_login_sends_code_to_normalized_number(client, messenger):
    resp = client.post("/login", data={"phone": "(570) 555-0100"})
    assert resp.status_code == 302 and resp.location.startswith("/login/verify")
    assert messenger.verifications == [ME]


def test_login_rejects_invalid_number(client, messenger):
    resp = client.post("/login", data={"phone": "12345"})
    assert "Enter a valid phone number" in resp.text
    assert messenger.verifications == []


def test_verify_without_pending_login_redirects(client):
    assert client.get("/login/verify").location == "/login"


def test_wrong_code_does_not_sign_in(client):
    client.post("/login", data={"phone": ME})
    resp = client.post("/login/verify", data={"code": "000000"})
    assert "didn" in resp.text
    assert db.session.query(User).count() == 0


def test_first_login_creates_account_and_goes_to_setup(client):
    resp = login(client)
    assert resp.location == "/preset/edit"
    assert db.session.query(User).one().phone == ME


def test_second_login_reuses_account(client):
    login(client)
    client.post("/logout")
    login(client)
    assert db.session.query(User).count() == 1


def test_login_follows_safe_next_only(client):
    client.post("/login?next=/preset", data={"phone": ME})
    assert client.post("/login/verify?next=/preset", data={"code": "123456"}).location == "/preset"

    client.post("/logout")
    client.post("/login?next=//evil.example", data={"phone": ME})
    resp = client.post("/login/verify?next=//evil.example", data={"code": "123456"})
    assert "evil" not in resp.location


def test_logout(logged_in):
    logged_in.post("/logout")
    assert "Get started" in logged_in.get("/").text


def test_pages_require_login(client):
    for path in ["/preset", "/preset/edit"]:
        assert client.get(path).location.startswith("/login")
    assert client.post("/sos").location.startswith("/login")
