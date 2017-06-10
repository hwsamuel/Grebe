from pymongo import MongoClient
from datetime import datetime
from province import Province, Provinces
import time, re

client = MongoClient()
BSIZE = 100000
EPOCH = '2016-07-14'

def get_tweets(start = None, end = None, keywords = None, fields = None, province = None):
    if fields == None:
        fields = 'id_str,text,collection_type,created_at,collected_at,user.id,user.screen_name,user.geo_enabled,user.location,coordinates.coordinates,place.full_name,place.country'
    
    fields = dict([(k, True) for k in fields.split(',')])
    fields['_id'] = False
    
    if start == None:
        start = datetime.strptime(EPOCH, '%Y-%m-%d')
    else:
        start = datetime.strptime(start, '%d-%m-%Y')
    
    if end == None:
        today = time.strftime("%Y-%m-%d")
        end = datetime.strptime(today, '%Y-%m-%d')
    else:
        end = datetime.strptime(end, '%d-%m-%Y')

    if end < start:
        raise Exception('The end date is before the start date')

    search = re.compile(keywords, re.I) if keywords else ""
    province = re.compile(province.value.name+"$", re.I) if province else ""
    tweets = client.grebe.tweets.find({"text": {'$regex': search}, "place.full_name": {'$regex': province}, 'coordinates.coordinates': {'$exists': True}, 'created_at': {'$gte': str(start), '$lte': str(end)}},projection=fields).batch_size(BSIZE)

    return list(tweets)