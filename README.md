# BeHerd

[![CI](https://github.com/arshnooramin/beherd/actions/workflows/ci.yml/badge.svg)](https://github.com/arshnooramin/beherd/actions/workflows/ci.yml)

A campus safety app that alerts your emergency contacts by SMS, either by holding an SOS button or by texting a codeword to a Twilio number. 

**Winner of the [2021 Twilio Hackathon](http://management.blogs.bucknell.edu/2021/04/19/twilio-challenge-winners/).**

<p>
  <img src="https://github.com/user-attachments/assets/39d4d6cd-d926-4009-b01e-16cbb9ec160d" alt="Landing page" width="200">
  <img src="https://github.com/user-attachments/assets/a63419c5-a8c3-48fb-a68b-13672635eeb1" alt="Home page with the SOS button" width="200">
  <img src="https://github.com/user-attachments/assets/20823f2c-268f-43ec-8cd9-0fa17fcf33d9" alt="Preset summary" width="200">
  <img src="https://github.com/user-attachments/assets/d7edcb03-4124-48d8-9c3c-b256f13f212d" alt="Editing a preset" width="200">
</p>

## How it works

1. A user signs in with their phone number using a one-time code (Twilio Verify). There are no passwords.
2. They set up a preset: their name, a codeword, an alert message, and 1–5 emergency contacts.
3. The alert goes out to every contact in either of two ways:
   - **SOS button**: holding the button on the home page sends it.
   - **Codeword**: texting the codeword *from the phone they signed in with* to the BeHerd number sends it. Twilio forwards the text to the `/sms` webhook, which looks the user up by the sending number, checks the codeword, and replies to confirm.

Built with Flask, SQLAlchemy, and Twilio.

## Getting started

Requires Python 3.10+.

```sh
git clone git@github.com:arshnooramin/beherd.git
cd beherd
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.sample .env  # set SECRET_KEY; MESSAGING_BACKEND=console needs nothing else
flask --app beherd run --debug
```

With `MESSAGING_BACKEND=console`, no texts are sent: sign-in codes and alerts are printed in the server log instead, so you can run the whole app without a Twilio account.

To send real texts, set `MESSAGING_BACKEND=twilio` and fill in the Twilio settings:

| Variable | Description |
| --- | --- |
| `SECRET_KEY` | Flask secret key, used for sessions and CSRF protection |
| `DATABASE_URL` | SQLAlchemy database URL. Defaults to SQLite at `instance/beherd.db` |
| `MESSAGING_BACKEND` | `twilio` (default) or `console` |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` | Twilio API credentials |
| `TWILIO_NUM` | Twilio phone number in E.164 format, e.g. `+15705550100` |
| `TWILIO_VERIFY_SID` | SID of a [Twilio Verify](https://www.twilio.com/docs/verify) service, used for sign-in codes |
| `DEFAULT_REGION` | Region for numbers entered without a country code. Defaults to `US` |

To receive texts, set the Twilio number's incoming-message webhook to `POST https://<your-host>/sms`. Requests are rejected unless they carry a valid Twilio signature. For local development, expose your server with a tunnel such as [ngrok](https://ngrok.com/).

Database tables are created on startup. There are no migrations yet; after a schema change, delete the database and let it be recreated.

## Development

```sh
pytest        # run the tests
black .       # format the code
```

CI runs both on every push and pull request; pull requests fail if the code isn't formatted with Black.

## Project layout

```
beherd/
  __init__.py   app factory
  auth.py       phone sign-in with one-time codes
  main.py       home page, SOS button, preset pages
  sms.py        Twilio webhook for codeword texts
  alerts.py     sending an alert to every contact
  messaging.py  Twilio and console backends for texts and verification
  models.py     User, Preset, Contact
  forms.py, phone.py, config.py, extensions.py
  templates/, static/
tests/
```

## Deployment

The app is a standard WSGI app, served in production with Gunicorn:

```sh
gunicorn "beherd:create_app()"
```

## Known limitations

- There is no rate limiting on sign-in codes or alerts beyond Twilio Verify's own limits.
- Alerts don't include location.
- There is no way to delete an account from the app.
