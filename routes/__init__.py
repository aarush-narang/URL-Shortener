import pymongo, certifi, os

global client

MONGO_DB_URI = os.getenv('MONGO_DB_URI')
client = pymongo.MongoClient(MONGO_DB_URI, tlsCAFile=certifi.where())  # you could also use sql db for this