from flask import Blueprint, render_template, redirect, request, jsonify, send_file, abort
import pymongo, os
import json
import hashlib
import re
import threading, time, datetime
import certifi
import random


MONGO_DB_URI = os.getenv('MONGO_DB_URI')
PROJ_PATH = os.getenv('PROJ_PATH')
client = pymongo.MongoClient(MONGO_DB_URI, tlsCAFile=certifi.where())  # you could also use sql db for this
db = client.url_shortener  # url_shortener is database name
requests = {}  # record all ip addresses and # of requests from each

class setInterval:  # this is like the setInterval function in javascript
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

def startInterval(t, func):  # start the interval and specify the time between each interval and what function to execute
    interval = setInterval(t, func)
    return interval

def endInterval(t, interval):  # end the interval after a specified amount of time and specify which interval to end
    timer = threading.Timer(t, interval.cancel)
    timer.start()

def setTimeout(t, func, args=None):  # this is like the setTimeout function in javascript
    timer = threading.Timer(t, func, args)
    timer.start()

def time_to_endofday(dt=None):  # number of seconds until the day ends
    if dt is None:
        dt = datetime.datetime.now()
    tomorrow = dt + datetime.timedelta(days=1)
    return (datetime.datetime.combine(tomorrow, datetime.time.min) - dt).total_seconds()


def short_link(link, char_length=7):
    # short link length
    char_length = 7
    if char_length > 128:
        raise ValueError(f'char_length {char_length} exceeds 128')

    # shuffle all chars that can be used
    chars = 'abcdefghijklmnopqrstuvqxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    chars = list(chars)
    random.shuffle(chars)
    chars = ''.join(chars)

    # generate the link
    hash_object = hashlib.sha512(link.encode())
    hash_hex = hash_object.hexdigest()
    new_link = hash_hex[0:char_length] + chars

    # take random section of the long string of chars
    lower_bound_max = len(new_link) - char_length - 1
    bound = random.randint(0, lower_bound_max)
    
    return new_link[bound:bound+char_length]


router = Blueprint(__name__, 'routes')
@router.route('/')
def home_redirect():
    return redirect('/home')


@router.route('/home')
def home():
    return render_template('home.html', domain=os.getenv('DOMAIN'), port=os.getenv('PORT'))


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
    # starting intervals that clear the number of requests per min/hr
    def clearMinuteNumbers():
        for addr in requests:
            requests[addr]['last_minute'] = 0

    def clearDayNumbers():
        for addr in requests:
            requests[addr]['last_day'] = 0

    def clearRateLimit():
        requests[ip_addr]['ratelimited'] = False

    startInterval(60, clearMinuteNumbers)
    startInterval(86400, clearDayNumbers)

    ip_addr = json.loads(data)['ip']  # ip addr from request

    if ip_addr not in requests:  # if the ip is new, add it
        requests[ip_addr] = { 'last_minute': 1, 'last_day': 1, 'ratelimited': False }
    elif requests[ip_addr]['ratelimited']:  # if ip is ratelimited, restrict them from making more requests
        return jsonify(ratelimited=True, msg='Youv\'e been ratelimited because you sent too many requests, try again later.')
    else:  # otherwise, increment their request count and then check if they exceed their limit of requests
        requests[ip_addr]['last_minute'] += 1
        requests[ip_addr]['last_day'] += 1
        if requests[ip_addr]['last_minute'] >= 1000:  # if the ip exceeds the max number of requests, restrict them from making more requests
            requests[ip_addr]['ratelimited'] = True
            requests[ip_addr]['last_minute'] = 0
            setTimeout(600, clearRateLimit)
            return jsonify(ratelimited=True, msg='Youv\'e been ratelimited because you sent too many requests, try again later.')
        if requests[ip_addr]['last_day'] >= 10000:  # if the ip exceeds the max number of requests, restrict them from making more requests
            requests[ip_addr]['ratelimited'] = True
            requests[ip_addr]['last_day'] = 0
            setTimeout(time_to_endofday(), clearRateLimit)
            return jsonify(ratelimited=True, msg='Youv\'e been ratelimited because you sent too many requests, try again later.')

    link_regex_1 = '(?!www\.)[a-zA-Z0-9._]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9._]*)'  # google.com
    link_regex_2 = '(www\.)[a-zA-Z0-9._]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9._]*)'  # www.google.com
    
    if re.match(link_regex_1, link) or re.match(link_regex_2, link):
        link = 'https://' + link
    

    # check if link is already in db
    link_check = db.urls.find({'link': link.lower() }) 
    for link in link_check:
        return jsonify(short_link=link['short_link'])
        
    # shorten the link
    short_url = short_link(link, link_size)  

    short_link_check = db.urls.find({'short_link': short_url})  # check if short link is already in db
    for db_link in short_link_check:  # if link already in db
        if link in db_link['link'] :  # check if the db link is the same they want
            return jsonify(short_link=db_link['short_link'])  #  if so return that short link
        else:
            while True:  # otherwise keep generating short links with 1 more character until it gets one not in the db
                new_link = short_link(link, link_size+1)
                link_check = db.urls.find({'short_link': new_link})
                old_db_link = ''
                for db_link in link_check:
                    old_db_link = db_link
                if old_db_link == new_link:
                    continue
                short_url = new_link
                break

    link_check = db.urls.find({'link': link}) # check if link is already in db
    for link in link_check:
        return jsonify(short_link=link['short_link'])

    db.urls.insert_one(
        { 'link': link, 'short_link': short_url }
    )
    return jsonify(short_link=short_url)


@router.get('/images/<img_name>')
def return_image(img_name):
    img_dir_path = os.path.dirname(f'{PROJ_PATH}\\images')

    for root, dirs, files in os.walk(img_dir_path):
        for file in files: 
            if file.endswith('.png') and img_name in file:
                return send_file(f'{PROJ_PATH}\\images\\{file}')
    return abort(404)


@router.get('/templates/<stylesheet>')
def return_stylesheet(stylesheet):
    stylesheet_dir_path = os.path.dirname(f'{PROJ_PATH}\\templates')

    for root, dirs, files in os.walk(stylesheet_dir_path):
        for file in files: 
            if file.endswith('.css') and stylesheet in file:
                return send_file(f'{PROJ_PATH}\\templates\\{file}')
    return abort(404)
