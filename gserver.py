from flask import Flask, render_template, request, Response, url_for, jsonify
from flask_httpauth import HTTPBasicAuth
from bson.json_util import dumps
from datetime import datetime, timedelta
from pymongo import MongoClient
import json, math, re, operator, pickle, os.path, time, hashlib

from province import Province, Provinces
from gexport import *
from gstats import *

MAX_DATE_RANGE = 30
BATCH_SIZE = 100000

app = Flask(__name__)
auth = HTTPBasicAuth()
out_file = None

from registered import *

def demo_data():
    demo_cache = ".cache/grebe/demo_data.p"
    if os.path.isfile(demo_cache):
        creation_time = os.path.getctime(demo_cache)
        if (time.time() - creation_time) // (24 * 3600) < MAX_DATE_RANGE:
            return pickle.load(open(demo_cache, "rb" ))
    
    num_dates = MAX_DATE_RANGE
    base = datetime.now() #base = datetime.strptime('26-7-2016','%d-%m-%Y')
    tweets = []
    end_date = None
    start_date = None
    for i in range(0,num_dates):
        start = (base - timedelta(days=2+i)).strftime("%d-%m-%Y")
        end = (base - timedelta(days=1+i)).strftime("%d-%m-%Y")
        start_date = start
        end_date = end if end_date == None else end_date
        tweets += demo_tweets(start,end, 2)
    
    pickle.dump([tweets, start_date, end_date], open(demo_cache, "wb"))
    return tweets, start_date, end_date

def demo_tweets(start, end, partition = 5):
    fields = 'coordinates.coordinates,text,place.full_name,created_at,user.screen_name'
    ab_tweets = get_tweets(start=start,end=end,province=Provinces.AB,fields=fields)
    bc_tweets = get_tweets(start=start,end=end,province=Provinces.BC,fields=fields)
    sk_tweets = get_tweets(start=start,end=end,province=Provinces.SK,fields=fields)
    mb_tweets = get_tweets(start=start,end=end,province=Provinces.MB,fields=fields)

    return ab_tweets[:partition] + bc_tweets[:partition] + sk_tweets[:partition] + mb_tweets[:partition]

def top_words():
    demo_tweets = demo_data()[0]
    f = open("glasgow")
    stop_words = [l.strip() for l in f.readlines()]
    dict = {}
    for tweet in demo_tweets:
        tokens = re.compile("[^a-zA-Z0-9']").split(tweet['text'].encode('punycode'))
        for t in tokens:
            t = t.lower().strip()
            if t in stop_words or len(t) < 2:
                continue
            if t in dict:
                dict[t] += 1
            else:
                dict[t] = 1
    dict = {k:v for k,v in dict.items() if v > 1}
    return sorted(dict.items(), key=operator.itemgetter(1), reverse=True)[:8]

@app.route('/grebe/')
def grebe():
    stats_cache = ".cache/grebe/stats.p"
    if os.path.isfile(stats_cache):
        creation_time = os.path.getctime(stats_cache)
        if (time.time() - creation_time) // (24 * 3600) < 7: # Weekly updates
            counts = pickle.load(open(stats_cache, "rb" ))
            return render_template('grebe/index.html',active='index',counts=counts)
    
    num_tweets = all_tweets().count()
    coord_tweets = tweets_with_coordinates().count()
    ab_tweets = tweets_in_province(Provinces.AB).count()
    sk_tweets = tweets_in_province(Provinces.SK).count()
    bc_tweets = tweets_in_province(Provinces.BC).count()
    mb_tweets = tweets_in_province(Provinces.MB).count()
    counts = [num_tweets,coord_tweets,ab_tweets,sk_tweets,bc_tweets,mb_tweets]
    pickle.dump(counts, open(stats_cache, "wb"))
    return render_template('grebe/index.html',active='index',counts=counts)

@app.route('/grebe/about/')
def about():
    return render_template('grebe/about.html',active='about')

@app.route('/grebe/api/demo/')
def api_demo():
    data = demo_data()
    demo_tweets = data[0]
    return render_template('grebe/demo/api.html',active='api',tweets=demo_tweets)

@app.route('/grebe/api/demo/json/')
def json_demo():
    data = demo_data()
    demo_tweets = data[0]
    start_date = data[1]
    end_date = data[2]
    
    out = '['
    for tweet in demo_tweets:
        out += str(json.dumps(tweet))+',\n'
    out = out[:-2]
    out += ']'
    return out

@app.route('/grebe/timemap/demo/')
def timemap_demo():
    data = demo_data()
    demo_tweets = data[0]
    if request.args.get('word'):
        filter_word = request.args.get('word').strip()
        
        sel_tweets = []
        for tweet in demo_tweets:
            txt = tweet['text'].encode('punycode')
            if re.search(filter_word, txt, re.IGNORECASE):
                sel_tweets.append(tweet)
            else:
                continue
    else:
        sel_tweets = demo_tweets
        filter_word = ""
    
    tw = top_words()
    return render_template('grebe/demo/timemap.html',active='timemap',tweets=sel_tweets,top_words=tw,selw=filter_word,custom=request.args.get('custom'))

@app.route('/grebe/graph/demo/')
def graph_demo():
    demo_tweets = demo_data()[0]
    dates = [d['created_at'].split()[0] for d in demo_tweets]
    unique_dates = list(set(dates))
    
    if request.args.get('word'):
        filter_word = request.args.get('word').strip()
        
        sel_tweets = []
        for tweet in demo_tweets:
            txt = tweet['text'].encode('punycode')
            if re.search(filter_word, txt, re.IGNORECASE):
                sel_tweets.append(tweet)
            else:
                continue
    else:
        sel_tweets = demo_tweets
        filter_word = ""
    
    if request.args.get('province'):
        province = request.args.get('province').strip()
        sel_prov = province
        province = Provinces[province].value.name
        old_sel_tweets = sel_tweets
        sel_tweets = []
        for tweet in old_sel_tweets:
            prov = tweet['place']['full_name']
            if re.search(province, prov, re.IGNORECASE):
                sel_tweets.append(tweet)
            else:
                continue
    else:
        sel_prov = ""

    tw = top_words()
    
    header = 'Date,'
    for k,v in tw:
        header += k + ','
    header = header [:-1]
            
    stats = ''
    for date in unique_dates:
        stats += date + ','
        for k,v in tw:
            count = 0
            for tweet in sel_tweets:
                cd = tweet['created_at'].split()[0]
                if date != cd:
                    continue
                txt = tweet['text'].encode('punycode')
                if re.search(k, txt, re.IGNORECASE):
                    count += 1
            stats += str(count) + ','
        stats = stats[:-1] + '\\n'
    
    tw = top_words()
    return render_template('grebe/demo/graph.html',active='graph',stats=stats,header=header,top_words=tw,selw=filter_word,sel_prov=sel_prov)
    
@app.route("/grebe/api/", methods=['GET'])
@auth.login_required
def api():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        
        start = datetime.strptime(start, '%d-%m-%Y')
        end =  datetime.strptime(end, '%d-%m-%Y')
        
        if end < start:
            raise Exception('The end date is before the start date')

        delta = end-start
        if delta.days > MAX_DATE_RANGE:
            raise Exception('The API supports a maximum range of ' + str(MAX_DATE_RANGE) + ' days')

        if request.args.get('province'):
            province = request.args.get('province')
            if province in [p.name for p in Provinces]:
                prov = re.compile(Provinces[province].value.name+"$", re.I)
            else:
                raise Exception('The Province code is invalid')
        else:
            raise Exception('The Province filter is required')

        if request.args.get('keywords'):
            keywords = request.args.get('keywords')
            search = re.compile(keywords, re.I)
        else:
            keywords = ""
            search = ""

        if request.args.get('fields'):
            fields = request.args.get('fields')
        else:
            fields = 'id_str,text,collection_type,created_at,collected_at,user.id,user.screen_name,user.geo_enabled,user.location,geo.coordinates,geo.coordinates,place.full_name,place.country'
        
        signature = '.cache/grebe/'+hashlib.sha1(str(start)+str(end)+province+keywords+fields).hexdigest()+'.p'
        if os.path.isfile(signature):
            out = pickle.load(open(signature, "rb" ))
        else:
            fields = dict([(k, True) for k in fields.split(',')])
            fields['_id'] = False    
            
            client = MongoClient()
            tweets = client.grebe.tweets.find({"text": {'$regex': search}, "place.full_name": {'$regex': prov}, 'coordinates.coordinates': {'$exists': True}, 'created_at': {'$gte': str(start), '$lte': str(end)}}, projection=fields).batch_size(BATCH_SIZE)

            out = '[' 
            for tweet in tweets:
                out += str(json.dumps(tweet))+',\n'
            out = out[:-2]
            out += ']'
            pickle.dump(out, open(signature, "wb"))

        generator = (cell for row in out for cell in row)
        return Response(generator, mimetype="text/plain", headers={"Content-Disposition":"attachment;filename="+out_file+".json"})
    except Exception as e:
        return 'Error: ' + str(e)

@auth.get_password
def get_pwd(username):
    global out_file
    out_file = username
    if username in USERS:
        return USERS.get(username)
    return None

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,threaded=True)