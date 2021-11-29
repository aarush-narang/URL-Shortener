__name__ = 'main' # have to change the name for some reason otherwise it wont import

from flask import Blueprint, render_template, session
import os
from routes import client

url_db = client.url_shortener  # url_shortener is collection name, contains the short link and main link, also contains user signin information (userid, username, password)

main_router = Blueprint(__name__, 'routes')

@main_router.route('/')
def home():
    if len(session) > 1: # check if there is a user id in their session
        try:
            db_user = url_db.users.find({ 'user_id': session['user']['user_id'] })[0]['username'] # if it matches, find the user and get the email
        except IndexError:
            del session['user']
            return render_template('home.html', domain=os.getenv('DOMAIN'), port=os.getenv('PORT')) # if it is unable to find in the db, delete the session (log out) and make them sign in again
        return render_template('home.html', domain=os.getenv('DOMAIN'), port=os.getenv('PORT'), user=db_user) # pass in the email when rendering template
    else:
        return render_template('home.html', domain=os.getenv('DOMAIN'), port=os.getenv('PORT'))
