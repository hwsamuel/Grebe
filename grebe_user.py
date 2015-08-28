'''
	Grebe - Alberta Online Social Chatter Monitor
	Retrieves Alberta-related tweets using Twitter Search and saves into SQLite database
	
	@author Hamman W. Samuel <hwsamuel@cs.ualberta.ca>	
	@todo Use Alberta city and town names retrieved from Geonames as terms in stream filter (for tweets without any geo-coordinates)
 	@todo Look up geo-location of keyword matches using Geonames service
'''

import tweepy
import json
import sqlite3
import datetime
import hashlib
import time

CONSUMER_KEY = 'rzCGw1Ckqqphfh4ZSfiOJ0x4e'
CONSUMER_SECRET = 'H28v274IGQbVnAl79k4FqLSaODiAbNpOyOWjvxXJPNivYkdgZ4'
ACCESS_TOKEN_KEY = '17213239-SxOg8JAXrceeZdWGqqSoc10kDKgNSeBmdYhmAjv5D'
ACCESS_TOKEN_SECRET = 'KTjKKYJIPINL8CD2QNxT4SA7rxHpwDC70vP11ngKeeW7y'
DATABASE = '/var/www/flask/grebe/grebe.db'

def search(self, data):
	decoded = json.loads(data)

	tweet = decoded['text']
	created_at = decoded['created_at']
	
	user_id = decoded['user']['id_str']
	screen_name = decoded['user']['screen_name']
	user_location = decoded['user']['location']
	user_time_zone = decoded['user']['time_zone']
	user_geo_enabled = decoded['user']['geo_enabled']
	user_verified = decoded['user']['verified']
	
	if 'place' in decoded and decoded['place']:
		tweet_place_country = decoded['place']['country']
		tweet_place_name = decoded['place']['full_name']
		tweet_place_type = decoded['place']['place_type']
	else:
		tweet_place_country = None
		tweet_place_name = None
		tweet_place_type = None
	
	retweeted = True if 'retweeted_status' in decoded and decoded['retweeted_status'] else False 
	quoted = True if 'quoted_status' in decoded and decoded['quoted_status'] else False
	
	if 'coordinates' in decoded and decoded['coordinates']:
		lng = decoded['coordinates']['coordinates'][0]
		lat = decoded['coordinates']['coordinates'][1]
	else:
		lng = None
		lat = None

	db = sqlite3.connect(DATABASE)
	cursor = db.cursor()
	today = datetime.datetime.now().date()
	tweet_hash = hashlib.sha1(tweet.encode('utf-8')).hexdigest()
	
	# Check if tweet exists by matching hash
	cursor.execute('SELECT id FROM tweets WHERE tweet_hash_id = ?', (tweet_hash,))
	if cursor.fetchone():
		print('Duplicate tweet ignored')
		return True # Ignore duplicate tweets
		
	# Save the tweet and related info to database
	cursor.execute('INSERT INTO tweets(tweet_hash_id,collected_at,created_at,user_id,screen_name,user_location,user_time_zone,user_geo_enabled,user_verified,tweet_place_country,tweet_place_name,tweet_place_type,retweeted,quoted,tweet,lng,lat) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (tweet_hash,today,created_at,user_id,screen_name,user_location,user_time_zone,user_geo_enabled,user_verified,tweet_place_country,tweet_place_name,tweet_place_type,retweeted,quoted,tweet,lng,lat))
	db.commit()

	return True
		
if __name__ == '__main__':
	keywords = ['vomit','diarrhea','cough','flu','fever'] # @todo Look up synonyms

	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)
	
	twitter_limit = 15
	end_correction = 1
	
	for word in keywords:
		try:
			results = api.search(q=word, geocode='53.54094,-113.49370,230km')
			stuff = api.user_timeline(screen_name = 'tmj_CAN_NURSING', count = 100, include_rts = True)
			
			count = 0
			for status in stuff:
				count += 1
				print(status.text)
			
			print count
			#for result in results:
			#	print result.created_at + '\n' + result.text
			
	  	except Exception as e:
	  		print e.message
	  		print("The program is still processing...")
	  		time.sleep(60*twitter_limit+end_correction)