from flask import Flask, render_template, flash, request, redirect, session
from twilio.rest import Client
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

account_sid = "AC3f0ad074e24c894cbde99008b467d1ba"
auth_token = "30b5003e14e356658633f53f7fd8c2c5"
client = Client(account_sid, auth_token)

app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class MainForm(Form):
    code_f = StringField('Codeword')
    name_f = StringField('Name')
    msg_f = TextAreaField('Message to Send')
    ph_1_f = StringField('Designated Contact #1')
    ph_2_f = StringField('Designated Contact #2')
    submit = SubmitField('Save')

@app.route("/", methods=['GET', 'POST'])
def get_data():
    form = MainForm(request.form)

    if request.method == 'POST':
        session['code'] = request.form['code_f']
        session['name'] = request.form['name_f']
        session['msg'] = request.form['msg_f']
        session['ph_1'] = request.form['ph_1_f']
        session['ph_2'] = request.form['ph_2_f']

    return render_template('hello.html', form=form)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = str(request.values.get('Body', None))

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body.lower() == session['code']:
        resp.message("[BeHerd]: Your designated contacts have been reached!")
        send_msg()

    return str(resp)

def send_msg():
    msg_1 = client.messages \
        .create(
                body="[BeHerd]: " + session['msg'] + " -" + session['name'],
                from_='+15707019176',
                to=session['ph_1']
            )
    msg_2 = client.messages \
        .create(
                body="[BeHerd]: " + session['msg'] + " -" + session['name'],
                from_='+15707019176',
                to=session['ph_2']
            )

if __name__ == "__main__":
    app.run(debug=True)