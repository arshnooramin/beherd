# BeHerd

## Purpose
Safety and comfort are backdrops for any thriving college community. BeHerd strives to push campuses to become safer by providing students a more flexible and accessible model of campus security. BeHerd allows students to control and ensure their safety from the comfort of their cell phones in a discrete and user-friendly manner.

BeHerd is an award-wining ([Twilio Challenge 2021 Winner](http://management.blogs.bucknell.edu/2021/04/19/twilio-challenge-winners/)) web application built using [Flask](https://flask.palletsprojects.com/en/2.1.x/) and [Twilio API](https://www.twilio.com/).

## Usage Example
Users can create personalized presets which include the following information:
   * Name/Identifier to be sent in the message
   * Custom coded message
   * Emergency contacts (upto 2, support for more will be added)
   * Codeword

This can be accomplished by visiting the [**Change Presets** route/page](https://beherd.herokuapp.com/preset) on the web app.

<img src="https://user-images.githubusercontent.com/38775985/165001173-9f33abd8-f67f-48be-821d-78cd7cd0d874.png" alt="drawing" width="200"/> <img src="https://user-images.githubusercontent.com/38775985/165001162-a8873e5d-9601-4065-88ba-ab9db1e768b3.png" alt="drawing" width="200"/>

Once a preset has been saved the emergency/designated contacts can be reached by tapping the SOS button on the [**Home** route/page](https://beherd.herokuapp.com/) of the web app

<img src="https://user-images.githubusercontent.com/38775985/165001178-7de208ae-5282-4181-bde1-e52db38b56d9.png" alt="drawing" width="200"/>

**OR** by sending the preset codeword to the Twilio number as a text message

<img src="https://user-images.githubusercontent.com/38775985/164998767-62369344-2747-4072-835d-3d5f301dc2dd.png" alt="drawing" width="200"/> <img src="https://user-images.githubusercontent.com/38775985/165001167-3112cf38-42e8-405a-977a-fada02ae485f.png" alt="drawing" width="200"/>
