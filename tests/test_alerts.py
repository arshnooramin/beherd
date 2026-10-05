from tests.conftest import FRIEND_1, FRIEND_2, make_preset


def test_landing_page_for_visitors(client):
    assert "Get started" in client.get("/").text


def test_sos_alerts_every_contact(logged_in, messenger):
    make_preset()
    resp = logged_in.post("/sos", follow_redirects=True)
    assert messenger.sent == [
        (FRIEND_1, "[BeHerd] I need help - Alex"),
        (FRIEND_2, "[BeHerd] I need help - Alex"),
    ]
    assert "Alert sent to all 2" in resp.text


def test_sos_with_a_single_contact(logged_in, messenger):
    make_preset(contacts=(FRIEND_1,))
    resp = logged_in.post("/sos", follow_redirects=True)
    assert "Alert sent to your contact." in resp.text
    assert "Ready to alert 1 contact<" in resp.text.replace("\n", "").replace("  ", "")


def test_sos_without_preset(logged_in, messenger):
    resp = logged_in.post("/sos")
    assert resp.location == "/preset/edit"
    assert messenger.sent == []


def test_sos_keeps_going_when_one_contact_fails(logged_in, messenger):
    make_preset()
    messenger.failing.add(FRIEND_1)
    resp = logged_in.post("/sos", follow_redirects=True)
    assert messenger.sent == [(FRIEND_2, "[BeHerd] I need help - Alex")]
    assert "Alert sent to 1 of 2" in resp.text


def test_sos_when_every_contact_fails(logged_in, messenger):
    make_preset()
    messenger.failing.update({FRIEND_1, FRIEND_2})
    resp = logged_in.post("/sos", follow_redirects=True)
    assert "call emergency services" in resp.text
