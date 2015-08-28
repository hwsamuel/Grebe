'''
	Grebe - Alberta Online Social Chatter Monitor
	Retrieves Alberta-related tweets using Twitter Search and saves into SQLite database
	
	@author Hamman W. Samuel <hwsamuel@cs.ualberta.ca>
'''

from tweepy import API
from grebe_lib import GrebeLib
from nltk.corpus import wordnet as wn
from tweepy.error import RateLimitError, TweepError
from tweepy.parsers import RawParser
from bson.json_util import loads as json_to_bson
from hashlib import sha1
from datetime import datetime
from pymongo.errors import DuplicateKeyError

class GrebeSearch():
	def __init__(self):
		self.grebe_lib = GrebeLib()
		
	def lookup(self,word):
		# Incircles inside Alberta area from http://www.freemaptools.com/radius-around-point.htm
		
		all_tweets = []
		try:
			api = API(self.grebe_lib.auth(),parser=RawParser())
			
			results = api.search(q=word,geocode='57.2505264790901,-114.9609375,305km')
			all_tweets.append(results)
			
			results = api.search(q=word,geocode='52.17123655103791,-113.5546875,270km')
			all_tweets.append(results)
		except Exception:
			self.grebe_lib.pause()

		return all_tweets
	
	def process(self):
		keywords = self.grebe_lib.load('static/search')
	
		used_words = []
		all_tweets = []
		for word in keywords:
	  		self.grebe_lib.respect()
			if word in used_words:
				continue
			else:
				used_words.append(word)
			
			all_tweets.append(self.get_tweets(word))
			
			synsets = wn.synsets(word)
			for synset in synsets:
				self.grebe_lib.respect()
				lemmas = synset.lemma_names()
				for lemma in lemmas:
					if '_' in lemma:
						continue
					
					if lemma in used_words:
						continue
					else:
						used_words.append(lemma)
					
					all_tweets.append(self.get_tweets(lemma))
	  	
		return all_tweets
	
	def get_tweets(self, word):
		tweets = self.lookup(word)[1]
		bson = json_to_bson(tweets)
		if len(bson['statuses']) > 0:
			return bson['statuses'][0]
		else:
			return None

	def save(self,all_tweets):
		today = datetime.now().date()
		for result in all_tweets:
			if result is None:
				continue
			
			text = result['text']
			text_hash = sha1(text.encode('utf-8')).hexdigest()
			result['collected_at'] = str(today)
			result['collection_type'] = 'search'
			
			try:
				if self.grebe_lib.collection.find_one({'text_hash': text_hash}) == None:
					self.grebe_lib.collection.insert_one(result)
				else:
					raise DuplicateKeyError()
			except DuplicateKeyError:
				print 'Skipped duplicate tweet'

if __name__ == '__main__':
	search = GrebeSearch()
	results = search.process()
	search.save(results)