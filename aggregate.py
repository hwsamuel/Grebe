#!/usr/bin/python

import tweepy, sys, json, traceback
from bson.json_util import loads as json_to_bson
from hashlib import sha1
from datetime import datetime
from pymongo import MongoClient
from time import sleep, strptime, mktime, time
from province import Province, Provinces
from authkey import AuthKey, AuthKeys

mode = None
province = None
client = MongoClient()
RATE_LIMIT = 15*60

class Stream(tweepy.StreamListener):
    def __init__(self):
        self.start_time = time()
        super(Stream, self).__init__()
        
    def on_status(self, data):
        if (time() - self.start_time) >= RATE_LIMIT:
            sys.exit()
        
        save(data)

    def on_error(self, code):
        print '[' + mode + ' - ' + province.name + '] ' + code
        sys.exit()

class Search:
    def __init__(self):
        self.start_time = time()
        
    def query(self, api, province):
        while True:
            if (time() - self.start_time) >= RATE_LIMIT:
                break

            try:
                tweets = api.search(q='place:'+province.value.id) # https://dev.twitter.com/rest/public/search-by-place
                for tweet in tweets:
                    save(tweet)
            except Exception as e:
                print '[' + mode + ' - ' + province.name + '] ' + str(e)
                break
        sys.exit()

    def get_province_id(self, api, province):
        # https://dev.twitter.com/rest/reference/get/geo/search
        return api.geo_search(query=province.value.name, granularity='admin')[0].id
    
def now():
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
def save(data):
    global mode
    global province
    
    bson = json_to_bson(json.dumps(data._json))
    tweet_date = strptime(bson['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
    tweet_date = str(datetime.fromtimestamp(mktime(tweet_date)))
    
    bson['created_at'] = tweet_date
    bson['text_hash'] = sha1(bson['text'].encode('punycode')).hexdigest()
    bson['collected_at'] = now()
    bson['collection_type'] = mode
    bson['province'] = province.name
    
    if client.grebe.tweets.find_one({'text_hash': bson['text_hash']}) == None:
        client.grebe.tweets.insert_one(bson)

def api(province):
    CONSUMER_KEY = AuthKeys[province.name].value.consumer_key
    CONSUMER_SECRET = AuthKeys[province.name].value.consumer_secret
    ACCESS_TOKEN_KEY = AuthKeys[province.name].value.access_token_key
    ACCESS_TOKEN_SECRET = AuthKeys[province.name].value.access_token_secret
    
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)

def main():
    global mode
    global province
    
    usage = '\nUsage: python aggregate.py [stream | search] [ON | QC | NS | NB | MB | BC | PE | SK | AB | NL]\n'
    
    if len(sys.argv) != 3:
        print usage
        return
    
    mode = sys.argv[1]
    try:
        province = Provinces[sys.argv[2].upper()]
    except Exception as e:
        print usage, str(e)
        return
    
    if mode == 'stream':
        mystream = tweepy.Stream(api(province).auth, Stream())
        mystream.filter(locations=province.value.geofence) # https://dev.twitter.com/streaming/overview/request-parameters#locations
    elif mode == 'search':
        mysearch = Search()
        mysearch.query(api(province), province)
    else:
        print usage

main()