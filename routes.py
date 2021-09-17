from flask import Blueprint, render_template, redirect, request, jsonify
import pymongo

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
    data = request
    print(data)
    # shorten link with an algo so that every link is unique based on their hash and then add to db
    return render_template('404.html')
