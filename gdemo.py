#!/usr/bin/python

from datetime import datetime, timedelta
from province import Province, Provinces
from gexport import *
from gstats import *
import sys, pickle, os.path, re, operator

HOME_DIR = '/home/ubuntu/.cache/grebe/' 
#HOME_DIR = '/home/hamman/Documents/PhD/Grebe/source/.cache/grebe/'
MAX_DATE_RANGE = 30

def demo_tweets(start, end, partition = 5):
    ab_tweets = get_tweets(start=start,end=end,province=Provinces.AB)
    bc_tweets = get_tweets(start=start,end=end,province=Provinces.BC)
    sk_tweets = get_tweets(start=start,end=end,province=Provinces.SK)
    mb_tweets = get_tweets(start=start,end=end,province=Provinces.MB)
    on_tweets = get_tweets(start=start,end=end,province=Provinces.ON)
    qc_tweets = get_tweets(start=start,end=end,province=Provinces.QC)
    return ab_tweets[:partition] + bc_tweets[:partition] + sk_tweets[:partition] + mb_tweets[:partition] + on_tweets[:partition] + qc_tweets[:partition]

def demo_data():
    demo_cache = HOME_DIR + "demo_data.p"
    num_dates = MAX_DATE_RANGE
    base = datetime.now()
    #base = datetime.strptime('26-7-2016','%d-%m-%Y')
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
    on_tweets = tweets_in_province(Provinces.ON)
    qc_tweets = tweets_in_province(Provinces.QC)
    counts = [num_tweets,coord_tweets,ab_tweets,sk_tweets,bc_tweets,mb_tweets,on_tweets,qc_tweets]
    pickle.dump(counts, open(stats_cache, "wb"))

def demo_tags():
    top_cache = HOME_DIR + "top_tags.p"
    demo_cache = HOME_DIR + "demo_data.p"
    if os.path.isfile(demo_cache):
        demo_tweets = pickle.load(open(demo_cache, "rb" ))
    else:
        return

    f = open("glasgow")
    stop_words = [l.strip() for l in f.readlines()]
    
    dict = {}
    for tweet in demo_tweets:
        tokens = re.compile("[^a-zA-Z0-9'#]").split(tweet[0])
        for t in tokens:
            t = t.lower().strip()
            if '#' not in t:
                continue
            if t in stop_words or len(t) <= 2:
                continue
            if t in dict:
                dict[t] += 1
            else:
                dict[t] = 1
    dict = {k:v for k,v in dict.items() if v > 1}
    tw = sorted(dict.items(), key=operator.itemgetter(1))[:10]
    ret = []
    for k,v in tw:
        ret.append(k)
    pickle.dump(ret, open(top_cache, "wb"))
    
if __name__ == "__main__":
    usage = '\nUsage: python gdemo.py [data | stats | tags]'
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
        elif mode == 'tags':
            demo_tags()
            print "Grebe top hashtags updated"
        else:
            print usage