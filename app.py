from flask import Flask, render_template, flash, request, redirect
from twilio.rest import Client
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

account_sid = "AC3f0ad074e24c894cbde99008b467d1ba"
auth_token = "30b5003e14e356658633f53f7fd8c2c5"
client = Client(account_sid, auth_token)

app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

name = "Undefined"
msg = "You have been reached out!"
ph_1 = "+14759991429"
ph_2 = '+19293889573'

class MainForm(Form):
    name_f = StringField('Name')
    msg_f = StringField('Message to Send')
    ph_1_f = StringField('Designated Contact #1')
    ph_2_f = StringField('Designated Contact #2')
    submit = SubmitField('Save')

@app.route("/", methods=['GET', 'POST'])
def hello():
    form = MainForm(request.form)

    # print(form.errors)

    if request.method == 'POST':
        name=form.name_f.data
        msg=form.msg_f.data
        ph_1=form.ph_1_f.data
        ph_2=form.ph_2_f.data

        print(name,msg,ph_1,ph_2)

    # if form.validate():
    #     # Save the comment here.
    #     print("Done")
    # else:
    #     flash('All the form fields are required. ')

    return render_template('hello.html', form=form)

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
                        body=msg,
                        from_='+15707019176',
                        to=ph_1
                    )
        msg_2 = client.messages \
                .create(
                        body=msg,
                        from_='+15707019176',
                        to=ph_2
                    )

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)