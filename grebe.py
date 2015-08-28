'''
    Grebe - Alberta Online Social Chatter Monitor
    Web app to query Alberta tweets index
    
    @author Hamman W. Samuel <hwsamuel@cs.ualberta.ca>    
    @todo Look up synonyms of filter words, and related senses, e.g. fever looks up headache, aches, etc.
    @todo Add Instagram, Snapchat to collections
'''
# -*- coding: utf-8 -*-
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from flask.testsuite.config import SECRET_KEY
from re import compile
from re import IGNORECASE
from jinja2 import evalcontextfilter, Markup, escape
from itertools import chain
from pymongo import MongoClient
from datetime import datetime
from time import strptime,mktime
from timeit import timeit
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from helper import *
from wordcloud.wordcloud import STOPWORDS
from lxml import html
import requests

DEBUG = True
SECRET_KEY = 'iwnCeK2hs7RL'

_paragraph_re = compile(r'(?:\r\n|\r|\n){2,}')
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('GREBE_SETTINGS', silent=True)

def synonyms(word):
    page = requests.get('http://moby-thesaurus.org/search?q=' + word)
    tree = html.fromstring(page.text)
    syns = tree.xpath('//ul[1]/li/a/text()')
    return syns[:3]

@app.template_filter()
@evalcontextfilter
def strip(eval_ctx, value):
    result = value.replace('\n','')
    result = result.replace('"',"'")
    result = result.replace('\r','')
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

def gen_wordcloud():
    med_words = load_file('static/med_words')
    mdb = get_mongo_db()
    collection = mdb.tweets
    all_tweets = list(collection.find())
    index = ''
    count = 0
    for tweet in all_tweets:
        tweet_tokens = [t for t in tokenize(tweet['text']) if t is not unicode('') and len(t) > 2]
        tweet_tokens = [t for t in tweet_tokens if t in med_words]
        index += ' '.join(tweet_tokens)
    
    STOPWORDS.add('https')
    STOPWORDS.add('amp')
    STOPWORDS.add('co')
    STOPWORDS.add('t')
    wc = WordCloud(background_color="white",stopwords=STOPWORDS)
    wc.generate(index)
    plt.imshow(wc)
    plt.axis("off")
    plt.show()

def get_mongo_db():
    client = MongoClient()
    return client.grebe
    
def shared():
    if request.method == 'POST' and request.form['filter_words']:
        filter_words = request.form['filter_words'].split(',')
    else:
        filter_words = []

    header = ',' + ','.join(filter_words) if len(filter_words) > 0 else ''    
    return [filter_words, header]

@app.route('/')
def default():
    return redirect(url_for('graph'))

@app.route('/wordcloud', methods=['POST', 'GET'])
def wordcloud():
    return render_template('wordcloud.html',active='wordcloud')

@app.route('/api', methods=['POST', 'GET'])
def api():
    head = shared()
    filter_words = head[0]
    header = head[1]
    
    mdb = get_mongo_db()
    collection = mdb.tweets
    
    all_tweets = []
    tweet_ids = []
    ignore = False
    for word in filter_words:
        tweets = list(collection.find({'text': compile('\\b' + word + '\\b', IGNORECASE)}, {'text':1, 'collected_at':1,'coordinates':1,'created_at':1}).sort('collected_at', -1))
        
        for row in tweets: # Ignore tweet if already covered by other keyword
            id = row['_id']
            if id in tweet_ids:
                ignore = True
            else:
                tweet_ids.append(id)
                ignore = False
        
        if ignore == True:
            continue
                 
        all_tweets.append(tweets)
    
    flat_tweets = flatten(all_tweets)
    unique_dates = collection.distinct('collected_at')

    return render_template('api.html',active='api',header=header,filter_words=filter_words,tweets=flat_tweets,unique_dates=unique_dates)

@app.route('/timemap', methods=['POST', 'GET'])
def timemap():
    head = shared()
    filter_words = head[0]
    header = head[1]
    
    mdb = get_mongo_db()
    collection = mdb.tweets
    
    themes = []
    all_tweets = []
    colors = ['red','yellow','green','blue','orange']
    i = 0
    unmappable = 0
    tweet_ids = []
    ignore = False
    for word in filter_words:
        tweets = list(collection.find({'coordinates': {'$ne':None},'text': compile('\\b' + word + '\\b', IGNORECASE)}, {'text':1, 'collected_at':1,'coordinates':1,'created_at':1}).sort('collected_at', -1))
        unmappable += collection.find({'coordinates': None,'text': compile('\\b' + word + '\\b', IGNORECASE)}).count()

        for row in tweets: # Ignore tweet if already covered by other keyword
            ids = row['_id']
            row['word'] = word
            row['theme'] = colors[i]
            if ids in tweet_ids:
                ignore = True
            else:
                tweet_ids.append(id)
                ignore = False
        
        if ignore == True:
            continue
                 
        themes.append([word,colors[i]])
        i += 1
        all_tweets.append(tweets)
    
    flat_tweets = flatten(all_tweets)
    flat_themes = flatten(themes)
    return render_template('timemap.html',unmappable=unmappable,themes=themes,header=header,tweets=flat_tweets,active='timemap')

@app.route('/graph', methods=['POST', 'GET'])
def graph():
    head = shared()
    filter_words = head[0]
    header = head[1]
    
    mdb = get_mongo_db()
    collection = mdb.tweets
    
    unique_dates = collection.distinct('created_at')
    
    stats = ""
    total_count = 0
    for date in unique_dates:
        stats += date + ','
        for word in filter_words:
            count = collection.find({'created_at': date, 'text': compile('\\b' + word + '\\b', IGNORECASE)},{'text':1, 'collected_at':1,'coordinates':1,'created_at':1}).count()
            total_count += count
            stats += str(count) + ','
        stats = stats[:-1] + '\\n'

    return render_template('graph.html',header=header,stats=stats,total_count=total_count,active='graph')

if __name__ == '__main__':
    app.run()