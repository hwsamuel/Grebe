from flask import Flask, render_template, request, Response, url_for
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
import re, operator, pickle, os.path, time, hashlib

from province import Province, Provinces
from registered import *

MAX_DATE_RANGE = 30
HOME_DIR = '/home/ubuntu/.cache/grebe/' 
#HOME_DIR = 'F:/PhD/Grebe/source/.cache/grebe/'

app = Flask(__name__)
auth = HTTPBasicAuth()
out_file = None

def demo_data():
    demo_cache = HOME_DIR + "demo_data.p"
    if os.path.isfile(demo_cache):
        creation_time = os.path.getctime(demo_cache)
        if (time.time() - creation_time) // (24 * 3600) < MAX_DATE_RANGE:
            return pickle.load(open(demo_cache, "rb" ))
    else:
        return None

def top_words():
    demo_tweets = demo_data()
    
    f = open("glasgow")
    stop_words = [l.strip() for l in f.readlines()]
    
    dict = {}
    for tweet in demo_tweets:
        tokens = re.compile("[^a-zA-Z0-9']").split(tweet[0])
        for t in tokens:
            t = t.lower().strip()
            if t in stop_words or len(t) < 2:
                continue
            if t in dict:
                dict[t] += 1
            else:
                dict[t] = 1
    dict = {k:v for k,v in dict.items() if v > 1}
    tw = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)[:8]
    ret = []
    for k,v in tw:
        ret.append(k)
    return ret

@app.route('/grebe/')
def grebe():
    counts = None
    stats_cache = HOME_DIR + "stats.p"
    if os.path.isfile(stats_cache):
        creation_time = os.path.getctime(stats_cache)
        if (time.time() - creation_time) // (24 * 3600) < 7: # Weekly updates
            counts = pickle.load(open(stats_cache, "rb" ))
    return render_template('grebe/index.html',active='index',counts=counts)
    
@app.route('/grebe/about/')
def about():
    return render_template('grebe/about.html',active='about')

@app.route('/grebe/api/demo/')
def api_demo():
    demo_tweets = demo_data()
    return render_template('grebe/demo/api.html',active='api',tweets=demo_tweets)

@app.route('/grebe/api/demo/json/')
def json_demo():
    demo_tweets = demo_data()
    fields = 'tweet, longitude, latitude, created_at, place_name'

    out = '[\n'
    for tweet in demo_tweets:
        i = 0
        out += "\t{\n"
        for field in fields.split(','):
            text = str(tweet[i])
            out += '\t\t"' + field.strip() + '":"' + text + '",\n'
            i += 1
        out = out[:-2] + "\n\t},\n"
    out = out[:-2]+'\n'
    
    if len(out.strip()) == 0:
        return ""
    else:
        out += ']'
        return out

@app.route('/grebe/timemap/demo/')
def timemap_demo():
    demo_tweets = demo_data()
    if request.args.get('word'):
        filter_word = request.args.get('word').strip()
        
        sel_tweets = []
        for tweet in demo_tweets:
            txt = tweet[0].encode('punycode')
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
    demo_tweets = demo_data()
    dates = [d[3] for d in demo_tweets]
    unique_dates = list(set(dates))
    
    if request.args.get('word'):
        filter_word = request.args.get('word').strip()
        
        sel_tweets = []
        for tweet in demo_tweets:
            txt = tweet[0].encode('punycode')
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
            prov = tweet[4]
            if re.search(province, prov, re.IGNORECASE):
                sel_tweets.append(tweet)
            else:
                continue
    else:
        sel_prov = ""

    if request.args.get('word'):
        tw = [request.args.get('word')]
    else:
        tw = top_words()
    
    header = 'Date,'
    for k in tw:
        header += k + ','
    header = header [:-1]
            
    stats = ''
    for date in unique_dates:
        date = str(date).split()[0]
        stats += date + ','
        for k in tw:
            count = 0
            for tweet in sel_tweets:
                cd = str(tweet[3]).split()[0]
                if date != cd:
                    continue
                txt = tweet[0].encode('punycode')
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

        if request.args.get('fields'):
            fields = request.args.get('fields')
        else:
            fields = 'tweet, longitude, latitude, created_at, place_name'
        
        strict_filter = "longitude Is Not Null AND latitude Is Not Null AND "
        qry = "SELECT " + fields + " FROM tweets WHERE " + strict_filter + " created_at >= '" + str(start) + "' AND created_at <= '" + str(end) + "'"
            
        if request.args.get('province'):
            province = request.args.get('province')
            if province in [p.name for p in Provinces]:
                prov = Provinces[province].value.name
                qry += " AND (place_name Like '%" + prov + "')"
            else:
                raise Exception('The Province code is invalid')
        else:
            raise Exception('The Province filter is required')

        if request.args.get('keywords'):
            keywords = request.args.get('keywords').lower().replace(' ','+')
            st = "tweet Like '%"
            keywords = keywords.replace('+', "%' AND " + st)
            keywords = keywords.replace('|', "%' OR " + st)
            qry += " AND (" + st + keywords + "%')"            
        else:
            keywords = ""
        
        signature = HOME_DIR+hashlib.sha1(str(start)+str(end)+province+keywords+fields).hexdigest()+'.p'
        if os.path.isfile(signature):
            out = pickle.load(open(signature, "rb" ))
        else:
            cursor.execute(qry)
            tweets = list(cursor)
            
            out = '[\n'
            for tweet in tweets:
                i = 0
                out += "\t{\n"
                for field in fields.split(','):
                    text = tweet[i]
                    if text == None:
                        text = ""
                    out += '\t\t"' + field.strip() + '":"' + str(text) + '",\n'
                    i += 1
                out = out[:-2] + "\n\t},\n"
            out = out[:-2]+'\n'
            pickle.dump(out, open(signature, "wb"))
        
        if request.args.get('download'):
            if request.args.get('download') == '1':
                generator = (cell for row in out for cell in row)
                return Response(generator, mimetype="text/plain", headers={"Content-Disposition":"attachment;filename="+out_file+".json"})
            else:
                return out
        else:
            return out
        
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