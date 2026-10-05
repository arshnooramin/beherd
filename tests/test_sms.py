import pytest
from twilio.request_validator import RequestValidator

from tests.conftest import FRIEND_1, FRIEND_2, ME, make_preset


def text(client, body, sender=ME, **kwargs):
    return client.post("/sms", data={"From": sender, "Body": body}, **kwargs)


def test_codeword_alerts_contacts(client, messenger):
    make_preset()
    resp = text(client, "  PineApple ")
    assert resp.mimetype == "application/xml"
    assert "Alert sent to all 2" in resp.text
    assert [to for to, _ in messenger.sent] == [FRIEND_1, FRIEND_2]


def test_wrong_codeword(client, messenger):
    make_preset()
    assert "Codeword not recognized" in text(client, "hello").text
    assert messenger.sent == []


def test_codeword_from_another_number_is_ignored(client, messenger):
    make_preset()
    assert "doesn't have a BeHerd preset" in text(client, "pineapple", sender=FRIEND_1).text
    assert messenger.sent == []


def test_codewords_are_per_user(client, messenger):
    make_preset(phone=ME, codeword="pineapple")
    make_preset(phone=FRIEND_1, contacts=(FRIEND_2, ME), codeword="pineapple")
    text(client, "pineapple", sender=FRIEND_1)
    assert [to for to, _ in messenger.sent] == [FRIEND_2, ME]


class TestSignature:
    @pytest.fixture(autouse=True)
    def require_signature(self, app):
        app.config["TWILIO_VALIDATE_SIGNATURE"] = True

    def test_unsigned_request_is_rejected(self, client, messenger):
        make_preset()
        assert text(client, "pineapple").status_code == 403
        assert messenger.sent == []

    def test_signed_request_is_accepted(self, client, messenger):
        make_preset()
        params = {"From": ME, "Body": "pineapple"}
        signature = RequestValidator("test-token").compute_signature("http://localhost/sms", params)
        resp = client.post("/sms", data=params, headers={"X-Twilio-Signature": signature})
        assert resp.status_code == 200
        assert len(messenger.sent) == 2

    def test_signature_uses_forwarded_https_url(self, client):
        make_preset()
        params = {"From": ME, "Body": "pineapple"}
        url = "https://beherd.example.com/sms"
        signature = RequestValidator("test-token").compute_signature(url, params)
        headers = {
            "X-Twilio-Signature": signature,
            "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "beherd.example.com",
        }
        assert client.post("/sms", data=params, headers=headers).status_code == 200
