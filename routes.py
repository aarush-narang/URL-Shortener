from flask import Blueprint, json, render_template, redirect, request, jsonify, send_file, abort
import pymongo
import json
import hashlib
import re
import os
import threading, time

MONGO_DB_URI = os.getenv('MONGO_DB_URI')
client = pymongo.MongoClient(MONGO_DB_URI)  # you could also use sql db for this
db = client.url_shortener  # url_shortener is database name


class setInterval:
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()

def startInterval(t, func):
    interval = setInterval(t, func)
    return interval

def endInterval(t, interval):
    timer = threading.Timer(t, interval.cancel)
    timer.start()


def short_link(link, char_length=7):  # make random instead of hash
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

    # ratelimiting
    # requests = {}  # record all ip addresses and # of requests from each
    # def clearMinuteNumbers():
    #     for addr in requests:
    #         requests[addr]['last_minute'] = 0

    # def clearDayNumbers():
    #     for addr in requests:
    #         requests[addr]['last_day'] = 0
    # startInterval(60, clearMinuteNumbers)
    # startInterval(86400, clearDayNumbers)

    # ip_addr = json.loads(data)['ip']  # ip addr from request

    # if ip_addr not in requests:
    #     requests[ip_addr] = { 'last_minute': 1, 'last_day': 1, 'ratelimited': False }
    # else:
    #     requests[ip_addr]['last_minute'] += 1
    #     requests[ip_addr]['last_day'] += 1
    #     if requests[ip_addr]['last_minute'] >= 6000:
    #         requests[ip_addr]['ratelimited'] = True
    #         return jsonify(valid='invalidURL', msg='Youv\'e been ratelimited because you sent too many requests.')


    # 'IP_ADDR': {
    #   'last_minute': 'num_of_requests_in_the_last_minute',
    #   'last_day': 'num_of_requests_in_the_day',
    #   'ratelimited': 'true/false if they are ratelimited or not'
    # }
    


    # check if link is valid
    if re.search('((http:\/\/)?127\.0\.0\.1:5000\/).+', link):
        return jsonify(valid='invalidURL', msg='That is already a shortened link!')

    link_regex_1 = '(?!www\.)[a-zA-Z0-9_]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9._]*)'  # google.com
    link_regex_2 = '(www\.)[a-zA-Z0-9_]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9._]*)'  # www.google.com
    link_regex_3 = '((http|https):\/\/)(?!www\.)[a-zA-Z0-9_]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9._]*)'  # https://google.com
    link_regex_4 = '((http|https):\/\/)(www\.)[a-zA-Z0-9_]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9._]*)'  # https://www.google.com

    if not re.match(link_regex_1, link) and not re.match(link_regex_2, link) and not re.match(link_regex_3, link) and not re.match(link_regex_4, link):
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

    # db.urls.insert_one(
    #     { 'link': link, 'short_link': short_url }
    # )
    return jsonify(short_link=short_url)


@router.get('/images/<img_name>')
def return_image(img_name):
    img_dir_path = os.path.dirname('C:\\Users\\Aarus\\PycharmProjects\\url-shortener-with-flask\\images')

    for root, dirs, files in os.walk(img_dir_path):
        for file in files: 
            if file.endswith('.png') and img_name in file:
                return send_file(f'C:\\Users\\Aarus\\PycharmProjects\\url-shortener-with-flask\\images\\{file}')
    return abort(404)


@router.get('/templates/<stylesheet>')
def return_stylesheet(stylesheet):
    stylesheet_dir_path = os.path.dirname('C:\\Users\\Aarus\\PycharmProjects\\url-shortener-with-flask\\templates')

    for root, dirs, files in os.walk(stylesheet_dir_path):
        for file in files: 
            if file.endswith('.css') and stylesheet in file:
                return send_file(f'C:\\Users\\Aarus\\PycharmProjects\\url-shortener-with-flask\\templates\\{file}')
    return abort(404)
