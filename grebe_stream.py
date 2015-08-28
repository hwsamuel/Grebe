'''
	Grebe - Alberta Online Social Chatter Monitor
	Retrieves Alberta-related tweets from the real-time Twitter stream and saves into SQLite database
	
	@author Hamman W. Samuel <hwsamuel@cs.ualberta.ca>
'''

from tweepy.streaming import StreamListener
from tweepy import Stream
from grebe_lib import GrebeLib
from bson.json_util import loads as json_to_bson
from hashlib import sha1
from datetime import datetime
from abpipsolver import AlbertaPIPSolver
#from bson.objectid import ObjectId

class GrebeListener(StreamListener):
	def __init__(self,grebe_lib):
		self.grebe_lib = grebe_lib
		
	def on_data(self, data):
		today = datetime.now().date()
		bson = json_to_bson(data)
		text = bson['text']
		text_hash = sha1(text.encode('utf-8')).hexdigest()
		
		bson['created_at'] = self.grebe_lib.tweet_to_pydate(bson['created_at']) # Modify date format to per-day
		bson['text_hash'] = text_hash
		bson['collected_at'] = str(today)
		bson['collection_type'] = 'stream'
		
		if bson['coordinates']:
			lng = bson['coordinates']['coordinates'][0]
			lat = bson['coordinates']['coordinates'][1]
			inAB = AlbertaPIPSolver().isWithinAlberta(lat,lng)
		else:
			inAB = True

		if self.grebe_lib.collection.find_one({'text_hash': text_hash}) == None and inAB == True:
			self.grebe_lib.collection.insert_one(bson)
		else:
			return True
	
	def on_error(self, statusCode):
		print("Error: %s" % (statusCode))
		if statusCode == 420 or statusCode == 429 or statusCode == 88:
			self.grebe_lib.pause()
	
	def on_timeout(self):
		raise TimeoutException()
	
	def on_limit(self, track):
		print("Message: %s" % (track))
		self.grebe_lib.pause()
		
class TimeoutException(Exception):
	pass

class GrebeStream():
	def __init__(self):
		self.grebe_lib = GrebeLib()

	def connect(self):
		auth = self.grebe_lib.auth()
		listener = GrebeListener(self.grebe_lib)
		return Stream(auth, listener)

	def process(self):
		# Polygon approximation of Alberta from http://boundingbox.klokantech.com

		twitter_stream = self.connect()
		while True:
			try:
				twitter_stream.filter(locations=[-120.0,49.0,-110.0,60.0])
			except KeyboardInterrupt:
				print("\nClosing stream\n")
				twitter_stream.disconnect()
				break
			except TimeoutException:
				print("\nRe-connecting to stream...\n")
				twitter_stream.disconnect()
				twitter_stream = self.connect()
				continue
			except Exception as e:
				print(str(e))
			
			self.grebe_lib.respect()
	
if __name__ == '__main__':
	stream = GrebeStream()
	stream.process()