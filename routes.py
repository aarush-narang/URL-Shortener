from flask import Blueprint, json, render_template, redirect, request, jsonify
import pymongo
import json

client = pymongo.MongoClient("mongodb+srv://Aarush:grxD7gx44ECwvpgv@url-shortener.dpgze.mongodb.net/url-shortener?retryWrites=true&w=majority")
db = client.url_shortener  # url_shortener is database name

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
    data = request.data.decode()
    link = json.loads(data)['link']

    
    short_url = 'test123'

    # shorten link with an algo so that every link is unique based on their hash
    
    db.urls.insert_one(
        { 'link': link, 'short_link': short_url}
    )
    return short_url
