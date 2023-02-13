from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, redirect, request, jsonify, session, abort
import os
from flask_wtf import CSRFProtect
import re
import pymongo
import json
import hashlib, random
import certifi, os
import threading, time, datetime

MONGO_DB_URI = os.getenv('MONGO_DB_URI')
client = pymongo.MongoClient(MONGO_DB_URI, tlsCAFile=certifi.where())  # you could also use sql db for this

url_db = client.url_shortener  # url_shortener is collection name, contains the short link and main link, also contains user signin information (userid, username, password)
last_user_id = {'user_id': '1000000000', 'run?': False} # store the last user id and if the function below was run in cache
requests = {}  # record all ip addresses and # of requests from each and the time they got ratelimted (to see how much longer their ratelimit will last)
DOMAIN = f'https://{os.getenv("DOMAIN")}:{os.getenv("PORT")}/'

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

csrf = CSRFProtect()
csrf.init_app(app)


# Error Handlers
@app.errorhandler(404)
def pagenotfound(e):
    return render_template('404.html')


# Main Routes
@app.route('/')
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


# Account Routes and Functions
def getLastDBUserId(): # store the last user_id from the db in memory and every time a new acct is created, increment by 1
    last_user = url_db.users.find({}).sort("user_id", pymongo.DESCENDING).limit(1)
    for x in last_user:
        last_user_id['user_id'] = x['user_id']

def generateSalt():
    # shuffle all chars that can be used
    chars = 'abcdefghijklmnopqrstuvqxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`~!@#$%^&*()-=_+[]\\{}|;\':",./<>?'
    chars = list(chars)
    random.shuffle(chars)
    chars = ''.join(chars)

    # take random section of the long string of chars
    lower_bound_max = len(chars) - 8
    bound = random.randint(0, lower_bound_max)
    
    return chars[bound:bound+7]


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        if len(session) > 1: # if they are already signed in, dont show the page
            return render_template('404.html')
        return render_template('sign_in.html')
    else:
        data = request.data.decode()
        data = json.loads(data)
        email = data['email']
        password = str(data['password'])
        pepper = str(os.getenv('PEPPER'))
        print(password)
        email_check = url_db.users.find({ 'email': email }) # check if email exists
        for user in email_check:
            salt = str(user['salt'])
            print(password, salt, pepper)
            if user['password'] == hashlib.sha256((password+salt+pepper).encode()).hexdigest(): # check if password matches email (if it exists)
                session['user'] = { 'user_id': user['user_id'], 'username': user['username'], 'email': user['email'] } # add user id to their session
                return jsonify(msg='LOGGED_IN')
            else:
                return jsonify(msg='INVALID_PASSWORD')

        return jsonify(msg='INVALID_EMAIL')

@app.get('/logout')
def logout():
    if len(session) > 1: # check if they are signed in
        del session['user']
    return redirect('/')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        if len(session) > 1: # if they are already signed in, dont show the page
            return render_template('404.html')
        return render_template('sign_up.html')
    else:
        if not last_user_id['run?']: # check if this func has already run
            getLastDBUserId() # if not, run it
            last_user_id['run?'] = True

        data = request.data.decode()
        data = json.loads(data)
        email = data['email']
        username = data['username']
        # check username and email with regex again
        username_regex = r'^[a-zA-Z0-9]{1,20}$'
        email_regex = r'^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
        if not re.match(username_regex, username):
            return jsonify(msg='INVALID_USERNAME')

        if not re.match(email_regex, email):
            return jsonify(msg='INVALID_EMAIL')

        # if both pass the regex, check if the username or email already exists
        username_check = url_db.users.find({ 'username': username }) # check if email exists
        for user in username_check:
            return jsonify(msg='EXISTING_USERNAME')
        email_check = url_db.users.find({ 'email': email }) # check if email exists
        for user in email_check:
            return jsonify(msg='EXISTING_EMAIL')
        password = data['password']
        last_user_id['user_id'] = str(int(last_user_id['user_id'])+1) # add on to the previous user id
        # get salt and pepper
        salt = generateSalt()
        pepper = str(os.getenv('PEPPER'))
        password = str(password)
        password = hashlib.sha256((password+salt+pepper).encode()).hexdigest() # hash password with salt and pepper

        url_db.users.insert_one(
            { 'user_id': last_user_id['user_id'], 'username': username, 'email': email, 'password': password, 'salt': salt }
        )
        url_db.user_urls.insert_one(
            { 'user_id': last_user_id['user_id'], 'links': [] }
        )
        return jsonify(msg='SIGNED_UP')

@app.get('/settings') # change to .route instead of .get and add methods for get and post, use this route for updating settings
def settings():
    if len(session) <= 1: # if they are not signed in, dont show the page
            return render_template('404.html')
    return render_template('settings.html', user=session['user']['username'])

@app.get('/mylinks')
def myLinks():
    if len(session) <= 1: # if they are not signed in, dont show the page
            return render_template('404.html')
    return render_template('mylinks.html', user=session['user']['username'], domain=os.getenv('DOMAIN'), port=os.getenv('PORT'))

@app.get('/getlinks')
def getLinks():
    if len(session) <= 1: # if they are not signed in, dont allow them to make requests
        return abort(401)
    user = url_db.user_urls.find_one({ 'user_id': session['user']['user_id'] })
    user_urls = dict(user)['links']
    return jsonify(links=user_urls)

@app.delete('/deletelink')
def deletelink():
    if len(session) <= 1: # if they are not signed in, dont show the page
        return abort(401)
    data = json.loads(request.data.decode())
    user = url_db.user_urls.find_one({ 'user_id': session['user']['user_id'] })
    user_links = dict(user)['links']
    for obj in user_links:
        if obj['link'] == data['link'] and obj['shortlink'] == data['shortlink']:
            user_links.remove(obj)
            url_db.user_urls.update_one({ 'user_id': session['user']['user_id'] }, { '$set': { 'links': user_links }  })
    return jsonify(msg='REMOVED_LINK')

# URL Shorten routes and functions
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


@app.route('/<short_link>')
def existing_link(short_link):
    redirect_url = url_db.urls.find({'short_link': short_link})
    for x in redirect_url:
        return redirect(x['link'])
    return render_template('404.html')


@app.post('/url_shorten')
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
    with open('banned.json', 'r') as f:
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


if __name__ == '__main__':
    app.run(host=os.getenv('DOMAIN'), port=os.getenv('PORT'), debug=True) # certificates for https