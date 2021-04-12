from flask import Flask, render_template, flash, request, redirect, session
from twilio.rest import Client
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from twilio.twiml.messaging_response import MessagingResponse
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)

account_sid = os.environ.get('account_sid')
auth_token = os.environ.get('auth_token')
client = Client(account_sid, auth_token)

app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.environ.get('secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://lsnznlhrwoydof:202f3c0a5ed662ce7672ca9d8f8fdc82f802fbb50b557fedb81ebf67faf9694a@ec2-35-174-35-242.compute-1.amazonaws.com:5432/dejij1924mip1"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Profile(db.Model):
    __tablename__ = "profile"

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    msg = db.Column(db.Text, nullable=False)
    ph_1 = db.Column(db.String(30), nullable=False)
    ph_2 = db.Column(db.String(30), nullable=False)

    def __init__(self, name, code, msg, ph_1, ph_2):
        self.name = name
        self.code = code
        self.msg = msg
        self.ph_1 = ph_1
        self.ph_2 = ph_2
    
    def __repr__(self):
        return '<Profile %r>' % self.name

class MainForm(Form):
    code_f = StringField('Codeword')
    name_f = StringField('Your Name')
    msg_f = TextAreaField('Message to Send')
    ph_1_f = StringField('Designated Contact #1')
    ph_2_f = StringField('Designated Contact #2')
    submit = SubmitField('Save')

@app.route("/", methods=['GET', 'POST'])
def home_view():
    if request.method == 'POST':
        profile = Profile.query.all()

        if len(profile) > 0:
            p = profile[-1]
            print(p.name, p.code, p.ph_1, p.ph_2)
            
            msg_1 = client.messages \
            .create(
                    body="[BeHerd]: " + p.msg + " - " + p.name,
                    from_='+15707019176',
                    to=p.ph_1
                )
            msg_2 = client.messages \
            .create(
                    body="[BeHerd]: " + p.msg + " - " + p.name,
                    from_='+15707019176',
                    to=p.ph_2
                )
    return render_template('home.html')

@app.route("/preset", methods=['GET', 'POST'])
def get_data():
    form = MainForm(request.form)

    if request.method == 'POST':
        data = Profile(request.form['name_f'], request.form['code_f'], \
            request.form['msg_f'], request.form['ph_1_f'], request.form['ph_2_f'])
        db.session.add(data)
        db.session.commit()

    return render_template('preset.html', form=form)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = str(request.values.get('Body', None))

    # Start our TwiML response
    resp = MessagingResponse()

    profile = Profile.query.all()

    if len(profile) > 0:
        p = profile[-1]
        print(p.name, p.code, p.ph_1, p.ph_2)

        # Determine the right reply for this message
        if body.lower() == p.code:
            resp.message("[BeHerd]: Your designated contacts have been reached!")
            msg_1 = client.messages \
            .create(
                    body="[BeHerd]: " + p.msg + " - " + p.name,
                    from_='+15707019176',
                    to=p.ph_1
                )
            msg_2 = client.messages \
            .create(
                    body="[BeHerd]: " + p.msg + " - " + p.name,
                    from_='+15707019176',
                    to=p.ph_2
                )
        else:
            resp.message("[BeHerd]: Codeword not found! Please set one up at https://be-herd-bucknell.herokuapp.com/")
        
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)