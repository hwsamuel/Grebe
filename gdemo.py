#!/usr/bin/python

from datetime import datetime, timedelta
from province import Province, Provinces
from gexport import *
from gstats import *
import sys, pickle

HOME_DIR = '/home/ubuntu/.cache/grebe/' 
#HOME_DIR = 'F:/PhD/Grebe/source/.cache/grebe/'
MAX_DATE_RANGE = 30

def demo_tweets(start, end, partition = 5):
    ab_tweets = get_tweets(start=start,end=end,province=Provinces.AB)
    bc_tweets = get_tweets(start=start,end=end,province=Provinces.BC)
    sk_tweets = get_tweets(start=start,end=end,province=Provinces.SK)
    mb_tweets = get_tweets(start=start,end=end,province=Provinces.MB)
    return ab_tweets[:partition] + bc_tweets[:partition] + sk_tweets[:partition] + mb_tweets[:partition]

def demo_data():
    demo_cache = HOME_DIR + "demo_data.p"
    num_dates = MAX_DATE_RANGE
    base = base = datetime.now() #datetime.strptime('26-7-2016','%d-%m-%Y')
    tweets = []
    end_date = None
    start_date = None
    for i in range(0,num_dates):
        start = (base - timedelta(days=2+i)).strftime("%d-%m-%Y")
        end = (base - timedelta(days=1+i)).strftime("%d-%m-%Y")
        start_date = start
        end_date = end if end_date == None else end_date
        tweets += demo_tweets(start,end, 2)   
    pickle.dump(tweets, open(demo_cache, "wb"))

def demo_stats():
    stats_cache = HOME_DIR + "stats.p"
    num_tweets = all_tweets()
    coord_tweets = tweets_with_coordinates()
    ab_tweets = tweets_in_province(Provinces.AB)
    sk_tweets = tweets_in_province(Provinces.SK)
    bc_tweets = tweets_in_province(Provinces.BC)
    mb_tweets = tweets_in_province(Provinces.MB)
    counts = [num_tweets,coord_tweets,ab_tweets,sk_tweets,bc_tweets,mb_tweets]
    pickle.dump(counts, open(stats_cache, "wb"))
    
if __name__ == "__main__":
    usage = '\nUsage: python gdemo.py [data | stats]'
    if len(sys.argv) != 2:
        print usage
    else:
        mode = sys.argv[1].strip().lower()
        if mode == 'data':
            demo_data()
            print "Demo data updated"
        elif mode == 'stats':
            demo_stats()
            print "Grebe stats updated"
        else:
            print usage