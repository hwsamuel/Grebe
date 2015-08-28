'''
	Grebe - Alberta Online Social Chatter Monitor
	Retrieves Alberta-related tweets from the real-time Twitter stream and saves into SQLite database
	
	@author Hamman W. Samuel <hwsamuel@cs.ualberta.ca>
'''

from tweepy import OAuthHandler
from datetime import datetime
from hashlib import sha1
from time import sleep,strptime,mktime
from timeit import timeit

from pymongo import MongoClient

CONSUMER_KEY = 'rzCGw1Ckqqphfh4ZSfiOJ0x4e'
CONSUMER_SECRET = 'H28v274IGQbVnAl79k4FqLSaODiAbNpOyOWjvxXJPNivYkdgZ4'
ACCESS_TOKEN_KEY = '17213239-SxOg8JAXrceeZdWGqqSoc10kDKgNSeBmdYhmAjv5D'
ACCESS_TOKEN_SECRET = 'KTjKKYJIPINL8CD2QNxT4SA7rxHpwDC70vP11ngKeeW7y'

class GrebeLib():
	def __init__(self):
		client = MongoClient()
		db = client.grebe
		self.collection = db.tweets

	def respect(self):
		sleep(5)
	
	def tweet_to_pydate(self,tweet_date):
	    time_struct = strptime(tweet_date, "%a %b %d %H:%M:%S +0000 %Y")
	    return str(datetime.fromtimestamp(mktime(time_struct)).date())
	
	def pause(self):
		print("[" + datetime.now() + "] Rate limit may have reached, pausing for 15 minutes...")
		twitter_limit = 15
		end_correction = 1
		sleep(60*twitter_limit+end_correction)

	def load(self, file):
		return [line.rstrip().lower() for line in open(file)]
	
	def auth(self):
		auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
		
		return auth
	
	def flatten(self,list_of_lists):
		return [val for sublist in list_of_lists for val in sublist]