from beherd.extensions import db
from beherd.models import Contact, Preset
from tests.conftest import FRIEND_1, FRIEND_2, FRIEND_3, ME, login, make_preset, preset_form


def test_view_redirects_to_setup_when_no_preset(logged_in):
    assert logged_in.get("/preset").location == "/preset/edit"


def test_create_preset(logged_in):
    resp = logged_in.post("/preset/edit", data=preset_form())
    assert resp.location == "/preset"

    preset = db.session.query(Preset).one()
    assert preset.codeword == "pineapple"
    assert [(c.name, c.phone) for c in preset.contacts] == [("Sam", FRIEND_1), (None, FRIEND_2)]


def test_up_to_five_contacts(logged_in):
    data = preset_form(**{f"contacts-{i}-phone": f"570555011{i}" for i in range(5)})
    logged_in.post("/preset/edit", data=data)
    assert db.session.query(Contact).count() == 5


def test_blank_rows_are_skipped(logged_in):
    data = preset_form(**{"contacts-1-phone": "", "contacts-3-phone": FRIEND_2})
    assert logged_in.post("/preset/edit", data=data).status_code == 302
    assert [c.phone for c in db.session.query(Preset).one().contacts] == [FRIEND_1, FRIEND_2]


def test_one_contact_is_enough(logged_in):
    data = preset_form(**{"contacts-1-phone": ""})
    assert logged_in.post("/preset/edit", data=data).status_code == 302
    assert [c.phone for c in db.session.query(Preset).one().contacts] == [FRIEND_1]


def test_requires_a_contact(logged_in):
    data = preset_form(**{"contacts-0-name": "", "contacts-0-phone": "", "contacts-1-phone": ""})
    resp = logged_in.post("/preset/edit", data=data)
    assert "Add an emergency contact" in resp.text
    assert db.session.query(Preset).count() == 0


def test_rejects_bad_contacts(logged_in):
    cases = {
        "not a number": "Enter a valid phone number",
        FRIEND_1: "already on the list",
        ME: "your own number",
    }
    for phone, error in cases.items():
        resp = logged_in.post("/preset/edit", data=preset_form(**{"contacts-1-phone": phone}))
        assert error in resp.text, phone
    resp = logged_in.post("/preset/edit", data=preset_form(**{"contacts-1-name": "Kim", "contacts-1-phone": ""}))
    assert "Add a phone number" in resp.text
    assert db.session.query(Preset).count() == 0


def test_rejects_reserved_codeword(logged_in):
    resp = logged_in.post("/preset/edit", data=preset_form(codeword="STOP"))
    assert "reserved" in resp.text


def test_edit_prefills_and_replaces_contacts(logged_in):
    make_preset(contacts=(FRIEND_1, FRIEND_2, FRIEND_3))
    page = logged_in.get("/preset/edit").text
    assert 'value="pineapple"' in page and 'value="(570) 555-0103"' in page

    data = preset_form(codeword="mango", **{"contacts-0-phone": FRIEND_3, "contacts-1-phone": FRIEND_2})
    logged_in.post("/preset/edit", data=data)
    preset = db.session.query(Preset).one()
    assert preset.codeword == "mango"
    assert [c.phone for c in preset.contacts] == [FRIEND_3, FRIEND_2]
    assert db.session.query(Contact).count() == 2


def test_view_shows_preset_with_masked_codeword(logged_in):
    make_preset()
    page = logged_in.get("/preset").text
    assert "[BeHerd] I need help - Alex" in page
    assert "(570) 555-0101" in page
    assert ">pineapple<" not in page


def test_users_only_see_their_own_preset(app, client):
    make_preset(phone=FRIEND_3)
    login(client)
    assert client.get("/preset").location == "/preset/edit"
    assert "No preset yet" in client.get("/").text
