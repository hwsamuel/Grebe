#!/usr/bin/python

from TwitterAPI import TwitterAPI, TwitterPager, TwitterRequestError, TwitterConnectionError
from hashlib import sha1
from datetime import datetime
from time import strptime, mktime
import mysql.connector as mariadb
import sys

from config import *

connector = mariadb.connect(user=DB_USER, password=DB_PWD, database=DB_NAME)

def _maybe_CA(data, strict = False):
	iso_CA = 'CA'
	
	if 'place' in data:
		place = data['place']
		if place is not None and 'country_code' in place:
			country_code = place['country_code']
		else:
			country_code = None
	else:
		country_code = None
	
	if strict and country_code == iso_CA:
		return True
	elif not strict and (country_code is None or country_code == iso_CA):
		return True
	else:
		return False
		
def verify(mode, iterator, strict = False):
	try:
		for tweet in iterator:
			if 'full_text' in tweet and _maybe_CA(tweet, strict):
				save(tweet, 'stream')
			elif 'message' in tweet:
				raise Exception('[%s] %s' % (mode, tweet['message']))
			elif 'limit' in tweet:
				raise Exception('[%s] %s' % (mode, tweet['limit']))
			elif 'disconnect' in tweet:
				raise Exception('[%s] %s' % (mode, tweet['disconnect']['reason']))
	except TwitterRequestError as tre:
		print str(tre)
	except TwitterConnectionError as tce:
		print str(tce)
	except mariadb.IntegrityError as msie:
		pass
	except Exception as e:
		print str(e)

def stream():
	api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	
	iterator = api.request('statuses/filter', {'locations': CANADA_SQUARES, 'tweet_mode':'extended'}).get_iterator()
	verify('stream', iterator, strict=True)

def search():
	api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, auth_type = 'oAuth2')
	
	cursor = connector.cursor()
	cursor.execute("SELECT hashtag FROM hashtags ORDER BY collected_at DESC LIMIT 20")
	hashtags = list(cursor)
	
	for region in CANADA_CIRCLES:
		qry = ' OR '.join(['%23'+h[0] for h in hashtags])
		qry = qry[:qry.rfind(" OR ", 0, 500)]
		iterator = TwitterPager(api, 'search/tweets', {'q': qry, 'geocode': region, 'count': 100, 'tweet_mode':'extended'}).get_iterator(wait=2)
		verify('search', iterator)

def status():
	api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, auth_type = 'oAuth2')
	
	for user in USERS:
		iterator = TwitterPager(api, 'statuses/user_timeline', {'screen_name': user, 'count': 200, 'tweet_mode':'extended'}).get_iterator(wait=2)        
		verify('status', iterator)
	
def _clean(str):
    if str == None:
        return None
    else:
        return str.encode('UTF-8').replace('\n', ' ')

def save(data, mode):
	if 'id_str' not in data:
		return

	cursor = connector.cursor()
	
	id = data['id_str']
	tweet = _clean(data['full_text'])
	tweet_hash = sha1(tweet).hexdigest()
	
	created_at = None
	if 'created_at' in data:
		created_at = data['created_at']
		created_at = strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y")
		created_at = str(datetime.fromtimestamp(mktime(created_at)))

	collected_at = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	collection_type = mode

	lang = None

	if 'lang' in data:
		lang = data['lang']

	place_name = None
	country_code = None

	if 'place' in data:
		place = data['place']
		if place is not None:
			place_name = (place['full_name'] if 'full_name' in place else None)
			country_code = (place['country_code'] if 'country_code' in place else None)

	user_id = None
	user_name = None
	user_geoenabled = None
	user_lang = None
	user_location = None
	user_timezone = None
	user_verified = None

	if 'user' in data:
		user = data['user']
		if user is not None:
			user_id = (user['id_str'] if 'id_str' in user else None)
			user_name = (user['screen_name'] if 'screen_name' in user else None)
			user_geoenabled = (user['geo_enabled'] if 'geo_enabled' in user else None)
			user_lang = (user['lang'] if 'lang' in user else None)
			user_location = (_clean(user['location']) if 'location' in user else None)
			user_timezone = (user['time_zone'] if 'time_zone' in user else None)
			user_verified = (user['verified'] if 'verified' in user else None)                

	longitude = None
	latitude  = None

	if 'coordinates' in data:
		coordinates = data['coordinates']
		if coordinates == None:
			longitude = None
			latitude  = None
		else:
			longitude = coordinates['coordinates'][0]
			latitude  = coordinates['coordinates'][1]

	tags = None
	entities = data['entities'] if 'entities' in data else None
	tags = entities['hashtags'] if entities is not None and 'hashtags' in entities else None

	for tag in tags:
		hashtag = tag['text'].lower().encode('UTF-8') if tag is not None and 'text' in tag else None
		if hashtag is None: continue
		cursor.execute("SELECT Count(tweet_id) FROM hashtags WHERE hashtag = Convert(%s Using utf8)", (hashtag,))
		if cursor.fetchone()[0] == 0:
			cursor.execute("INSERT INTO hashtags(tweet_id,hashtag,created_at,collected_at) VALUES(%s,%s,%s,%s)", (id,hashtag,created_at,collected_at))
			connector.commit()					

	cursor.execute("SELECT Count(id) FROM tweets WHERE tweet_hash = %s", (tweet_hash,))
	if cursor.fetchone()[0] == 0:
		cursor.execute("INSERT INTO tweets(id,tweet,tweet_hash,longitude,latitude,created_at,collected_at,collection_type,lang,place_name,country_code,user_id,user_name,user_geoenabled,user_lang,user_location,user_timezone,user_verified) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (id,tweet,tweet_hash,longitude,latitude,created_at,collected_at,collection_type,lang,place_name,country_code,user_id,user_name,user_geoenabled,user_lang,user_location,user_timezone,user_verified))
		connector.commit()
	else:
		return

if __name__ == '__main__':
	usage = '\nUsage: python spyder.py [status | search | stream]'

	if len(sys.argv) != 2:
		print usage
	else:
		mode = sys.argv[1].lower()
		if mode == 'status':
			status()
		elif mode == 'search':
			search()
		elif mode == 'stream':
			stream()
		else:
			print usage