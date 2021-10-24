__name__ = 'main' # have to change the name for some reason otherwise it wont import

from flask import Blueprint, render_template, redirect, send_file, abort, session, make_response
import os
from routes import client
import re

PROJ_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
url_db = client.url_shortener  # url_shortener is collection name, contains the short link and main link, also contains user signin information (userid, username, password)

main_router = Blueprint(__name__, 'routes')

@main_router.route('/')
def home_redirect():
    return redirect('/home')


@main_router.route('/home')
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


@main_router.get('/<dir>/<resource>')
def return_file(dir, resource):
    file_ending = re.split('\.', resource).pop() # get the file type
    file_dir_path = os.path.dirname(f'{PROJ_PATH}\\{dir}')

    if dir != 'public':
        file_dir_path = os.path.dirname(f'{PROJ_PATH}\\src\\templates\\{dir}')

    for root, dirs, files in os.walk(file_dir_path): # walk through the dir
        for file in files: 
            if file.endswith(f'.{file_ending}') and resource in file: # find the file and send it
                return send_file(f'{file_dir_path}\\{dir}\\{file}')
    return make_response(render_template('404.html'), 404) # if file was not found, send 404 code and render 404 page
