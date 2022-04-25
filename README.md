# BeHerd

Campus safety application powered by Twilio - [beherd.herokuapp.com](https://beherd.herokuapp.com/)

## Purpose
Safety and comfort are backdrops for any thriving college community. BeHerd strives to push campuses to become safer by providing students a more flexible and accessible model of campus security. BeHerd allows students to control and ensure their safety from the comfort of their cell phones in a discrete and user-friendly manner.

BeHerd is an award-wining ([Twilio Challenge 2021 Winner](http://management.blogs.bucknell.edu/2021/04/19/twilio-challenge-winners/)) web application built using [Flask](https://flask.palletsprojects.com/en/2.1.x/) and [Twilio API](https://www.twilio.com/).

## Installation
Given below are the instructions for setting up this project locally:
* Clone this repository
```
git clone git@github.com:arshnooramin/beherd.git
cd beherd
```
* Create a Python virtual environment and install dependencies
```
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
* Create a [Twilio Developer Account](https://www.twilio.com/try-twilio), set up a Twilio phone number, and get API credentials
* Set up a SQL database and get URI and secret key (can be set up locally)
* Create an `.env` file by copying `.env.sample`, add Twilio and database credentials to the `.env` file
* Run web app on `localhost`
```
flask run
```
* Configure Twilio phone number to make a POST request to Webhook URL
<img src="https://twilio-cms-prod.s3.amazonaws.com/images/configure-webhook_RJaWU8n.width-800.png" alt="drawing" width="400"/>

## Project Structure
* **`static`**: Includes `style.css` for custom styling of the frontend of the web app. This project utilizes the [Bootstrap](https://getbootstrap.com/) CSS framework for most of its styling. stylesheets can be expanded or additional stylesheets can be added to change the look, feel, and responsiveness of the web app.
* **`templates`**: includes *child* HTML for each route in the web app (`preset.html` for `/preset` and `home.html` for `/`) in addition to the *parent* HTML - `base.html` which the *child* HTML files inherit from. These can be edited to change the structure of the web app/pages or additional child templates can be added for new functionalities. For example, if authentication was being added to store user's presets, a new HTML would be required with a login form.
* **`app.py`**: is the main Flask app containing instructions for web app routing, updating the database, and making requests to the Twilio API.

## Usage Example
Users can create personalized presets which include the following information:
   * Name/Identifier to be sent in the message
   * Codeword
   * Custom coded message
   * Emergency contacts (upto 2, support for more will be added)

This can be accomplished by visiting the [**Change Presets** route/page](https://beherd.herokuapp.com/preset) on the web app.

<img src="https://user-images.githubusercontent.com/38775985/165001173-9f33abd8-f67f-48be-821d-78cd7cd0d874.png" alt="drawing" width="200"/> <img src="https://user-images.githubusercontent.com/38775985/165001162-a8873e5d-9601-4065-88ba-ab9db1e768b3.png" alt="drawing" width="200"/>

Once a preset has been saved the emergency/designated contacts can be reached by tapping the SOS button on the [**Home** route/page](https://beherd.herokuapp.com/) on the web app

<img src="https://user-images.githubusercontent.com/38775985/165001178-7de208ae-5282-4181-bde1-e52db38b56d9.png" alt="drawing" width="200"/> <img src="https://user-images.githubusercontent.com/38775985/164998767-62369344-2747-4072-835d-3d5f301dc2dd.png" alt="drawing" width="200"/>

**OR** by sending the preset codeword to the Twilio number as a text message

<img src="https://user-images.githubusercontent.com/38775985/165001167-3112cf38-42e8-405a-977a-fada02ae485f.png" alt="drawing" width="200"/> <img src="https://user-images.githubusercontent.com/38775985/164998767-62369344-2747-4072-835d-3d5f301dc2dd.png" alt="drawing" width="200"/>

## How It Works?
The application has three main components: a **SQL database**, **Flask web app**, and **Twilio API**. Users created presets are stored on a SQL database. When a message is sent to the BeHerd Twilio number a POST request is made by Twilio to the web app’s server:
```
POST https://beherd.herokuapp.com/sms
```
which then calls a Python function. The function retrieves data from the database and checks whether the text that was sent was a valid codeword. If a valid codeword was found, texts are sent to the designated contacts of the user with the set message via the Twilio Python module. The messages can also be triggered using the SOS button on the web app itself.

<img src="https://user-images.githubusercontent.com/38775985/165004942-16a8733a-6239-4d81-bfaa-56e402d57e04.png" alt="drawing"/>

