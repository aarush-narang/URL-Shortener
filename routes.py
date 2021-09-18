from flask import Blueprint, json, render_template, redirect, request
import pymongo
import json
import hashlib

client = pymongo.MongoClient('mongodb+srv://Aarush:grxD7gx44ECwvpgv@url-shortener.dpgze.mongodb.net/url-shortener?retryWrites=true&w=majority')

db = client.url_shortener  # url_shortener is database name

def short_link(link, char_length=8):
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
    link_size = 6  # the number of characters at the end of the link example.com/thisstuff
    data = request.data.decode()  # request data, the link they want to shorten
    link = json.loads(data)['link']  # convert from json to dict
    short_url = short_link(link, link_size)  # shorten the link

    short_link_check = db.urls.find({'short_link': short_url})  # check if link is already in db
    for db_link in short_link_check:  # if link already in db
        if db_link['link'] == link:  # check if the db link is the same they want
            return db_link['link']  #  if so return that short link
        else:
            while True:  # otherwise keep generating short links with 1 more character until it gets one not in the db
                new_link = short_link(link, link_size+1)
                link_check = db.urls.find({'short_link': new_link})
                for db_link in link_check:
                    if db_link['link'] != link:
                        link_size += 1
                        continue
                return new_link


    link_check = db.urls.find({'link': link})
    for link in link_check:
        return link['short_link']


    db.urls.insert_one(
        { 'link': link, 'short_link': short_url}
    )
    return short_url
