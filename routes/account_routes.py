__name__ = 'accounts' # have to change the name for some reason otherwise it wont import

import re
from flask import Blueprint, render_template, redirect, request, jsonify, session
import pymongo, certifi, os
import json

MONGO_DB_URI = os.getenv('MONGO_DB_URI')
PROJ_PATH = os.getenv('PROJ_PATH')
client = pymongo.MongoClient(MONGO_DB_URI, tlsCAFile=certifi.where())  # you could also use sql db for this
url_db = client.url_shortener  # url_shortener is collection name, contains the short link and main link, also contains user signin information (userid, username, password)
last_user_id = {'user_id': '1000000000', 'run?': False} # store the last user id and if the function below was run in cache


def getLastDBUserId(): # store the last user_id from the db in memory and every time a new acct is created, increment by 1
    last_user = url_db.users.find({}).sort("user_id", pymongo.DESCENDING).limit(1)
    for x in last_user:
        last_user_id['user_id'] = x['user_id']

account_router = Blueprint(__name__, 'routes')


@account_router.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        if len(session) > 1: # if they are already signed in, redirect them back to home
            return redirect('/home')
        return render_template('sign_in.html')
    else:
        data = request.data.decode()
        data = json.loads(data)
        email = data['email']
        encrypted_password = data['password']

        email_check = url_db.users.find({ 'email': email }) # check if email exists
        for user in email_check: 
            if user['password'] == encrypted_password: # check if password matches email (if it exists)
                session['user_id'] = user['user_id'] # add user id to their session
                return jsonify(msg='LOGGED_IN')
            else:
                return jsonify(msg='INVALID_PASSWORD')

        return jsonify(msg='INVALID_EMAIL')


@account_router.get('/logout')
def logout():
    if len(session) > 1: # check if they are signed in
        del session['user_id']
    return redirect('/home')

@account_router.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        if len(session) > 1: # if they are already signed in, redirect them back to home
            return redirect('/home')
        return render_template('sign_up.html')
    else:
        if not last_user_id['run?']:
            getLastDBUserId()
            last_user_id['run?'] = True

        data = request.data.decode()
        data = json.loads(data)
        email = data['email']
        username = data['username']
        # check username and email with regex again
        username_regex = r'^[a-zA-Z0-9]{1,20}$'
        email_regex = r'^(?! )(?=(.*[a-z]){3,})(?=(.*[A-Z]){2,})(?=(.*[0-9]){2,})(?=(.*[!@#$%^&*()\-__+.]){1,}).{8,}(?<! )$'
        if not re.match(username_regex, username):
            return jsonify(msg='INVALID_USERNAME')

        if not re.match(email_regex, username):
            return jsonify(msg='INVALID_EMAIL')

        # if both pass the regex, check if the username or email already exist
        username_check = url_db.users.find({ 'username': username }) # check if email exists
        for user in username_check:
            return jsonify(msg='EXISTING_USERNAME')
        email_check = url_db.users.find({ 'email': email }) # check if email exists
        for user in email_check:
            return jsonify(msg='EXISTING_EMAIL')
        password = data['password']
        last_user_id['user_id'] = str(int(last_user_id['user_id'])+1) # add on to the previous user id
        url_db.users.insert_one(
            { 'user_id': last_user_id['user_id'], 'username': username, 'email': email, 'password': password }
        )
        return jsonify(msg='SIGNED_UP')


@account_router.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html')
    else:
        return jsonify(msg='received')

@account_router.route('/mylinks', methods=['GET', 'POST'])
def mylinks():
    if request.method == 'GET':
        return render_template('mylinks.html')
    else:
        return jsonify(msg='received')