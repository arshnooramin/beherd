from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body.lower() == 'hello':
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