'''
	Generic search using keywords from a file
	@author Hamman W. Samuel <hwsamuel@ualberta.ca>
'''

from tweepy import API
from grebe_lib import GrebeLib
from tweepy.error import RateLimitError, TweepError
from tweepy.parsers import RawParser
from bson.json_util import loads as json_to_bson
from hashlib import sha1
from datetime import datetime
from pymongo.errors import DuplicateKeyError

class KeywordSearch():
	def __init__(self):
		self.grebe_lib = GrebeLib()
		
	def lookup(self,word):
		all_tweets = []
		try:
			api = API(self.grebe_lib.auth(),parser=RawParser())
			
			results = api.search(q=word)
			all_tweets.append(results)
		except Exception:
			self.grebe_lib.pause()

		return all_tweets
	
	def process(self,keywords_file):
		keywords = self.grebe_lib.load(keywords_file)
	
		used_words = []
		all_tweets = []
		for word in keywords:
	  		self.grebe_lib.respect()
			if word in used_words:
				continue
			else:
				used_words.append(word)
			
			all_tweets.append(self.get_tweets(word))
			
		return all_tweets
	
	def get_tweets(self, word):
		found_tweets = self.lookup(word)
		tweets = found_tweets[0]
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
	search = KeywordSearch()
	results = search.process('search_keywords')
	search.save(results)