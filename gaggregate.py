#!/usr/bin/python

import tweepy, sys, json, traceback
from bson.json_util import loads as json_to_bson
from hashlib import sha1
from datetime import datetime
from time import sleep, strptime, mktime, time
from province import Province, Provinces
from authkey import AuthKey, AuthKeys
import mysql.connector as mariadb

mode = None
province = None
RATE_LIMIT = 15*60
mariadb_connection = mariadb.connect(user='root', password='', database='grebe')
cursor = mariadb_connection.cursor(buffered=True)

class Stream(tweepy.StreamListener):
    def __init__(self):
        self.start_time = time()
        super(Stream, self).__init__()
        
    def on_status(self, data):
        if (time() - self.start_time) >= RATE_LIMIT:
            mariadb_connection.close()
            sys.exit()
        
        save(data)

    def on_error(self, code):
        print '[' + mode + ' - ' + province.name + '] ' + code
        mariadb_connection.close()
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
        mariadb_connection.close()
        sys.exit()

    def get_province_id(self, api, province):
        # https://dev.twitter.com/rest/reference/get/geo/search
        return api.geo_search(query=province.value.name, granularity='admin')[0].id
    
def now():
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
def clean(str):
    if str == None:
        return None
    else:
        return str.encode('punycode')[:-1].replace('\n', ' ')

def save(data):
    global mode
    global province
    
    bson = json_to_bson(json.dumps(data._json))

    if 'id_str' not in bson or 'text' not in bson:
        return
        
    id = bson['id_str']
    tweet = clean(bson['text'])
    tweet_hash = sha1(tweet).hexdigest()
    
    if 'created_at' in bson:
        created_at = bson['created_at']
        created_at = strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y")
        created_at = str(datetime.fromtimestamp(mktime(created_at)))
    else:
        created_at = None
    
    collected_at = now()
    collection_type = mode
    
    if 'lang' in bson:
        lang = bson['lang']
    else:
        lang = None
    
    if 'place' in bson:
        place = bson['place']
        if 'full_name' in place:
            place_name = place['full_name']
        else:
            place_name = None
        if 'country_code' in place:
            country_code = place['country_code']
        else:
            country_code = None
    else:
        place_name = None
        country_code = None
        
    cronjob_tag = province.name
    
    if 'user' in bson:
        user = bson['user']
        if 'id_str' in user:
            user_id = user['id_str']
        else:
            user_id = None
        
        if 'screen_name' in user:
            user_name = user['screen_name']
        else:
            user_name = None
            
        if 'geo_enabled' in user:
            user_geoenabled = user['geo_enabled']
        else:
            user_geoenabled = None
            
        if 'lang' in user:
            user_lang = user['lang']
        else:
            user_lang = None
        
        if 'location' in user:
            user_location = clean(user['location'])
        else:
            user_location = None
        
        if 'time_zone' in user:
            user_timezone = user['time_zone']
        else:
            user_timezone = None
            
        if 'verified' in user:
            user_verified = user['verified']
        else:
            user_verified = None
    else:
        user_id = None
        user_name = None
        user_geoenabled = None
        user_lang = None
        user_location = None
        user_timezone = None
        user_verified = None
    
    if 'coordinates' in bson:
        coordinates = bson['coordinates']
        if coordinates == None:
            longitude = None
            latitude  = None
        else:
            longitude = coordinates['coordinates'][0]
            latitude  = coordinates['coordinates'][1]
    else:
        longitude = None
        latitude  = None
        
    cursor.execute("SELECT id FROM tweets WHERE tweet_hash = %s", (tweet_hash,))
    if cursor.fetchone():
        return
    else:
        cursor.execute("INSERT INTO tweets(id,tweet,tweet_hash,longitude,latitude,created_at,collected_at,collection_type,lang,place_name,country_code,cronjob_tag,user_id,user_name,user_geoenabled,user_lang,user_location,user_timezone,user_verified) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (id,tweet,tweet_hash,longitude,latitude,created_at,collected_at,collection_type,lang,place_name,country_code,cronjob_tag,user_id,user_name,user_geoenabled,user_lang,user_location,user_timezone,user_verified))
    
        mariadb_connection.commit()

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
    
    usage = '\nUsage: python gaggregate.py [stream | search] [ON | QC | NS | NB | MB | BC | PE | SK | AB | NL | NU | NT | YT]\n'
    
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