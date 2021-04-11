from flask import Flask, request, redirect
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

account_sid = "AC3f0ad074e24c894cbde99008b467d1ba"
auth_token = "30b5003e14e356658633f53f7fd8c2c5"
client = Client(account_sid, auth_token)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = str(request.values.get('Body', None))

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body.lower() == 'hello':
        resp.message("Your designated contacts have been reached!")
        msg_1 = client.messages \
                .create(
                        body="Arsh reached out!",
                        from_='+15707019176',
                        to='+14759991429'
                    )
        msg_2 = client.messages \
                .create(
                        body="Arsh reached out!",
                        from_='+15707019176',
                        to='+19293889573'
                    )

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)