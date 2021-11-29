__name__ = 'routes' # have to change the name for some reason otherwise it wont import

import os
from flask import Blueprint, render_template, redirect, request, jsonify, session
import json
import hashlib, random
import re
import threading, time, datetime

from routes import client 

url_db = client.url_shortener  # url_shortener is collection name, contains the short link and main link, also contains user signin information (userid, username, password)
requests = {}  # record all ip addresses and # of requests from each and the time they got ratelimted (to see how much longer their ratelimit will last)
DOMAIN = f'https://{os.getenv("DOMAIN")}:{os.getenv("PORT")}/'

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
    hash_object = hashlib.sha256(link.encode())
    hash_hex = hash_object.hexdigest()
    new_link = hash_hex[0:char_length] + chars

    # take random section of the long string of chars
    lower_bound_max = len(new_link) - char_length - 1
    bound = random.randint(0, lower_bound_max)
    
    return new_link[bound:bound+char_length]


url_shorten_router = Blueprint(__name__, 'routes')


@url_shorten_router.route('/<short_link>')
def existing_link(short_link):
    redirect_url = url_db.urls.find({'short_link': short_link})
    for x in redirect_url:
        return redirect(x['link'])
    return render_template('404.html')


@url_shorten_router.post('/url_shorten')
def url_shorten():
    link_size = 7  # the number of characters at the end of the link example.com/thisstuff
    data = request.data.decode()  # request data, the link they want to shorten
    data = json.loads(data) # convert from json to dict

    ip_addr = data['ip']  # ip address from request
    link = data['link'] # link they entered
    
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

    if len(session) > 1:
        max_reqs_min = 100
        max_reqs_day = 1500
    else:
        max_reqs_min = 20
        max_reqs_day = 400

    if ip_addr not in requests:  # if the ip is new, add it
        requests[ip_addr] = { 'last_minute': 1, 'last_day': 1, 'ratelimited': False, 'ratelimit_off_time': None }
    elif requests[ip_addr]['ratelimited']:  # if ip is ratelimited, restrict them from making more requests
        return jsonify(error=True, type='RATELIMITED', msg=f'Youv\'e been ratelimited because you sent too many requests, try again later.') # after {round(requests[ip_addr]["ratelimit_off_time"] - time.time(), 1)} seconds
    else:  # otherwise, increment their request count and then check if they exceed their limit of requests
        requests[ip_addr]['last_minute'] += 1
        requests[ip_addr]['last_day'] += 1
        if requests[ip_addr]['last_minute'] > max_reqs_min:  # if the ip exceeds the max number of requests, restrict them from making more requests
            requests[ip_addr]['ratelimited'] = True
            requests[ip_addr]['last_minute'] = 0
            requests[ip_addr]['ratelimit_off_time'] = time.time() + 600
            setTimeout(600, clearRateLimit)
            return jsonify(error=True, type='RATELIMITED', msg=f'Youv\'e been ratelimited because you sent too many requests, try again later.') # after {round(requests[ip_addr]["ratelimit_off_time"] - time.time(), 1)} seconds
        if requests[ip_addr]['last_day'] > max_reqs_day:  # if the ip exceeds the max number of requests, restrict them from making more requests
            requests[ip_addr]['ratelimited'] = True
            requests[ip_addr]['last_day'] = 0
            requests[ip_addr]['ratelimit_off_time'] = time.time() + time_to_endofday()
            setTimeout(time_to_endofday(), clearRateLimit)
            return jsonify(error=True, type='RATELIMITED', msg=f'Youv\'e been ratelimited because you sent too many requests, try again later.') # after {round(requests[ip_addr]["ratelimit_off_time"] - time.time(), 1)} seconds

    link_regex_1 = r'(?!www\.)[a-zA-Z0-9._]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9._]*)'  # google.com
    link_regex_2 = r'(www\.)[a-zA-Z0-9._]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9._]*)'  # www.google.com
    
    if re.match(link_regex_1, link) or re.match(link_regex_2, link):
        link = 'http://' + link
    

    # check if domain/link is banned
    with open('./banned.json', 'r') as f:
        banned = json.load(f)
        
    for domain in banned['domains']:
        if domain in link:
            return jsonify(error=True, msg='That domain is banned.')

    for specific_link in banned['links']:
        if specific_link == link:
            return jsonify(error=True, msg='That link is banned.')

    def insertLinkToUserDB(long_link, shortlink): # inserts link into their collection of stored links
        if len(session) > 1:
            user_urls = url_db.user_urls.find_one({ 'user_id': session['user']['user_id'] })
            user_urls = list(dict(user_urls)['links'])
            if len(user_urls) == 200:
                return 'LIMIT_REACHED'
            if len(user_urls) == 0:
                user_urls.append({ 'link': long_link, 'shortlink': shortlink })
                url_db.user_urls.update_one({ 'user_id': session['user']['user_id'] }, { '$set': { 'links': user_urls }  })
            isInDb = False
            for obj in user_urls:
                if obj['link'] == long_link:
                    isInDb = True
                    break
            if not isInDb:
                user_urls.append({ 'link': long_link, 'shortlink': shortlink })
                url_db.user_urls.update_one({ 'user_id': session['user']['user_id'] }, { '$set': { 'links': user_urls }  })

    # check if link is already in db
    link_check = url_db.urls.find({'link': link }) 
    for db_link_full in link_check:
        res = insertLinkToUserDB(link, db_link_full['short_link'])
        if res == 'LIMIT_REACHED':
            return jsonify(short_link=db_link_full['short_link'], error=True, type='LIMIT_REACHED', msg='Oops! Youv\'e reached your limit for storing links, delete some links to be able to store more!')
        return jsonify(short_link=db_link_full['short_link'])

    # shorten the link
    short_url = short_link(link, link_size)  

    short_link_check = url_db.urls.find({'short_link': short_url})  # check if short link is already in db
    for db_link_short in short_link_check:  # if link already in db
        if link in db_link_short['link'] :  # check if the db link is the same they want
            res = insertLinkToUserDB(link, db_link_short['short_link'])
            if res == 'LIMIT_REACHED':
                return jsonify(short_link=db_link_short['short_link'], error=True, type='LIMIT_REACHED', msg='Oops! Youv\'e reached your limit for storing links, delete some links to be able to store more!')
            return jsonify(short_link=db_link_short['short_link'])
        else:
            while True:  # otherwise keep generating short links with 1 more character until it gets one not in the db
                new_link = short_link(link, link_size+1)
                link_check = url_db.urls.find({'short_link': new_link})
                old_db_link = ''
                for db_link_short in link_check:
                    old_db_link = db_link_short
                if old_db_link == new_link:
                    continue
                short_url = new_link
                break

    url_db.urls.insert_one(
        { 'link': link, 'short_link': short_url }
    )
    res = insertLinkToUserDB(link, short_url)
    if res == 'LIMIT_REACHED':
        return jsonify(short_link=short_url, error=True, type='LIMIT_REACHED', msg='Oops! Youv\'e reached your limit for storing links, delete some links to be able to store more!')
    return jsonify(short_link=short_url)
