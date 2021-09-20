from flask import Blueprint, json, render_template, redirect, request, jsonify, send_file
import pymongo
import json
import hashlib
import re
import os

from werkzeug.exceptions import abort

MONGO_DB_URI = os.getenv('MONGO_DB_URI')
client = pymongo.MongoClient(MONGO_DB_URI)  # you could also use sql db for this

db = client.url_shortener  # url_shortener is database name

def short_link(link, char_length=7):
    if char_length > 128:
        raise ValueError(f'char_length {char_length} exceeds 128')
    hash_object = hashlib.sha512(link.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex[0:char_length]


router = Blueprint(__name__, 'routes')

@router.route('/')
def home_redirect():
    return redirect('/home')


@router.route('/home')
def home():
    return render_template('home.html')


@router.route('/<short_link>')
def existing_link(short_link):
    redirect_url = db.urls.find({'short_link': short_link})
    for x in redirect_url:
        return redirect(x['link'])
    return render_template('404.html')


@router.post('/url_shorten')
def url_shorten():
    link_size = 7  # the number of characters at the end of the link example.com/thisstuff
    data = request.data.decode()  # request data, the link they want to shorten
    link = json.loads(data)['link']  # convert from json to dict

    # check if link is valid
    if re.search('((http:\/\/)?127\.0\.0\.1:5000\/).+', link):
        return jsonify(valid='invalidURL', msg='That is already a shortened link!')

    full_link_regex = "((http|https):\/\/)(www.)?[a-zA-Z0-9@:%._\+~#?&\/=]{2,256}\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\+~#?&\/=]*)"
    if not re.match(full_link_regex, link):
        if '.' not in link:
            return jsonify(valid='invalidURL', msg='Please enter a valid URL!')
        if not re.search('(http|https)', link):
            # if re.match('^.+(www.)?[a-zA-Z0-9@:%._\+~#?&\/=]{2,256}.+$', link):  # FIX THIS REGEX, make sure people cant put ://test.com, ;//test.com or anything like that in the input
            #     return jsonify(valid='invalidURL', msg='Please enter a valid URL!')
            link = 'https://' + link
        else:
            return jsonify(valid='invalidURL', msg='Please enter a valid URL!')
    

    short_url = short_link(link, link_size)  # shorten the link

    short_link_check = db.urls.find({'short_link': short_url})  # check if short link is already in db
    for db_link in short_link_check:  # if link already in db
        if link in db_link['link'] :  # check if the db link is the same they want
            return jsonify(short_link=db_link['short_link'])  #  if so return that short link
        else:
            while True:  # otherwise keep generating short links with 1 more character until it gets one not in the db
                new_link = short_link(link, link_size+1)
                link_check = db.urls.find({'short_link': new_link})
                for db_link in link_check:
                    if db_link['link'] != link:
                        link_size += 1
                        continue
                return jsonify(short_link=new_link)


    link_check = db.urls.find({'link': link}) # check if link is already in db
    for link in link_check:
        return jsonify(short_link=link['short_link'])

    db.urls.insert_one(
        { 'link': link, 'short_link': short_url }
    )
    return jsonify(short_link=short_url)

@router.get('/images/<img_name>')
def return_image(img_name):
    img_dir_path = os.path.dirname('C:\\Users\\Aarus\\PycharmProjects\\url-shortener-with-flask\\images')

    for root, dirs, files in os.walk(img_dir_path):
        for file in files: 
            if file.endswith('.png') and img_name in file:
                return send_file(f'C:\\Users\\Aarus\\PycharmProjects\\url-shortener-with-flask\\images\\{file}')
    return abort(404)