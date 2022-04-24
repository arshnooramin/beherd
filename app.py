# import the Flask module
from flask import *

# import the Twilio REST Client API
from twilio.rest import Client

# import the wtforms module
from wtforms import Form, TextAreaField, StringField, SubmitField

# import the MessagingResponse module from Twilio
from twilio.twiml.messaging_response import MessagingResponse

# import the Flask SQLAlchemy module
from flask_sqlalchemy import SQLAlchemy

# import decouple module
from decouple import config

# initiate the flask app
app = Flask(__name__)

# get Twilio credentials from env file
account_sid = config('ACCOUNT_SID')
auth_token = config('AUTH_TOKEN')
twilio_num = config('TWILIO_NUM')

# initiate a Twilio client with retrieved credentials
client = Client(account_sid, auth_token)

# initiate a config object for SQLAlchemy database
app.config.from_object(__name__)

# get the SQLAlchemy database credentials from env file
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config('SQLALCHEMY_TRACK_MODIFICATIONS', cast=bool)

# initiate the SQLAlchemy database object
db = SQLAlchemy(app)

# Initiate a preset model/database table to store user data
class Preset(db.Model):
    __tablename__ = "preset"

    # identifier
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # name of the user
    name = db.Column(db.String(100), nullable=False)
    # codeword used to send/initiate the emergency message
    code = db.Column(db.String(100), nullable=False)
    # message to be sent
    msg = db.Column(db.Text, nullable=False)
    # emergency contacts
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

# The main form class to update the Preset model/table
class MainForm(Form):
    code_f = StringField('Codeword')
    name_f = StringField('Your Name')
    msg_f = TextAreaField('Message to Send')
    ph_1_f = StringField('Designated Contact #1')
    ph_2_f = StringField('Designated Contact #2')
    submit = SubmitField('Save')

"""Request to be made on the home page view"""
@app.route("/", methods=['GET', 'POST'])
def home_view():
    if request.method == 'POST':
        # extract all the data from the Preset model/table
        preset = Preset.query.all()

        # if Preset model/table is not empty
        if len(preset) > 0:
            # get the most recent data
            p = preset[-1]
            
            # send message to each emergency contact
            client.messages.create(
                body="[BeHerd]: " + p.msg + " - " + p.name,
                from_=twilio_num,
                to=p.ph_1
            )
            client.messages.create(
                body="[BeHerd]: " + p.msg + " - " + p.name,
                from_=twilio_num,
                to=p.ph_2
            )
    # render home.html for route -> '/'
    return render_template('home.html')

"""Request to be made on the home page view"""
@app.route("/preset", methods=['GET', 'POST'])
def get_data():
    # get the data from the HTML form on the webpage
    form = MainForm(request.form)

    if request.method == 'POST':
        # Create a new row/entry in the Preset model/table with user entered data
        data = Preset(request.form['name_f'], request.form['code_f'], \
            request.form['msg_f'], request.form['ph_1_f'], request.form['ph_2_f'])
        db.session.add(data)
        db.session.commit()

    # render preset.html for route -> '/preset'
    return render_template('preset.html', form=form)

"""Request to be made on the sms page view"""
@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent to the Twilio number
    body = str(request.values.get('Body', None))

    # Start our TwiML response
    resp = MessagingResponse()

    # # extract all the data from the Preset model/table
    preset = Preset.query.all()

    # if Preset model/table is not empty
    if len(preset) > 0:
        # get the most recent data
        p = preset[-1]

        # if incoming message from user corresponds to the saved codeword
        if body.lower() == p.code:
            # notify user that the emergency contacts have been reached
            resp.message("[BeHerd]: Your designated contacts have been reached!")
            
            # send message to each emergency contact
            client.messages \
            .create(
                body="[BeHerd]: " + p.msg + " - " + p.name,
                from_=twilio_num,
                to=p.ph_1
            )
            client.messages \
            .create(
                body="[BeHerd]: " + p.msg + " - " + p.name,
                from_=twilio_num,
                to=p.ph_2
            )
        # if incoming message did not correspond to a set codeword notify and instruct user to set one
        else:
            resp.message(
                "[BeHerd]: Codeword not found! Please set one up at https://be-herd-bucknell.herokuapp.com/"
            )   
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)