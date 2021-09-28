__name__ = 'main' # have to change the name for some reason otherwise it wont import

from flask import Blueprint, render_template, redirect, send_file, abort, session
import os
from routes import client

PROJ_PATH = os.getenv('PROJ_PATH')
url_db = client.url_shortener  # url_shortener is collection name, contains the short link and main link, also contains user signin information (userid, username, password)

main_router = Blueprint(__name__, 'routes')

@main_router.route('/')
def home_redirect():
    return redirect('/home')


@main_router.route('/home')
def home():
    if len(session) > 1: # check if there is a user id in their session
        db_user = url_db.users.find({ 'user_id': session['user_id'] })[0]['username'] # if it matches, find the user and get the email
        return render_template('home.html', domain=os.getenv('DOMAIN'), port=os.getenv('PORT'), user=db_user) # pass in the email when rendering template
    else:
        return render_template('home.html', domain=os.getenv('DOMAIN'), port=os.getenv('PORT'))


@main_router.get('/images/<img_name>')
def return_image(img_name):
    img_dir_path = os.path.dirname(f'{PROJ_PATH}\\images')

    for root, dirs, files in os.walk(img_dir_path):
        for file in files: 
            if file.endswith('.png') and img_name in file:
                return send_file(f'{PROJ_PATH}\\images\\{file}')
    return abort(404)


@main_router.get('/templates/stylesheets/<stylesheet>')
def return_stylesheet(stylesheet):
    stylesheet_dir_path = os.path.dirname(f'{PROJ_PATH}\\templates\\stylesheets')

    for root, dirs, files in os.walk(stylesheet_dir_path):
        for file in files: 
            if file.endswith('.css') and stylesheet in file:
                return send_file(f'{PROJ_PATH}\\templates\\stylesheets\\{file}')
    return abort(404)
