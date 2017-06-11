from datetime import datetime
from pymongo import MongoClient
from province import Province, Provinces
import re

client = MongoClient()
BSIZE = 100000

def all_tweets():
    return client.grebe.tweets.find().batch_size(BSIZE)

def tweets_with_coordinates():
    return client.grebe.tweets.find({'coordinates.coordinates': {'$exists':True}}).batch_size(BSIZE)

def tweets_in_province(province):
    province = re.compile(province.value.name+"$", re.I)
    return client.grebe.tweets.find({'coordinates.coordinates': {'$exists':True}, "place.full_name": {'$regex': province}}).batch_size(BSIZE)

def main():
    print 'Total Tweets: '+str(all_tweets().count())
    print 'Tweets with coordinates: '+str(tweets_with_coordinates().count())
    
    provinces = [Provinces.AB, Provinces.SK, Provinces.BC, Provinces.MB]
    for province in provinces:
        tweets = tweets_in_province(province)
        print 'Tweets from ' + province.value.name + ': ' + str(tweets.count())

if __name__ == "__main__":
    main()