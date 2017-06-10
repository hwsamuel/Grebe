from enum import Enum

class AuthKey():
    def __init__(self,consumer_key,consumer_secret,access_token_key,access_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret

# Twitter Auth Keys Sign Up https://apps.twitter.com/
class AuthKeys(Enum):
    AB = AuthKey(
        consumer_key='key here', 
        consumer_secret='key here', 
        access_token_key='key here', 
        access_token_secret='key here')
    
    BC = AB
    SK = AB