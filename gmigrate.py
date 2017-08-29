import mysql.connector as mariadb
from pymongo import MongoClient

def clean(str):
    if str == None:
        return None
    else:
        return str.encode('punycode')[:-1].replace('\n', ' ')
    
mariadb_connection = mariadb.connect(user='root', password='', database='grebe')
cursor = mariadb_connection.cursor(buffered=True)

client = MongoClient()
table = client.grebe.tweets.find().batch_size(100000)
for row in table:
    if 'id_str' not in row:
        continue
        
    id = row['id_str']

    cursor.execute("SELECT id FROM tweets WHERE id = %s", (id,))
    if cursor.fetchone():
        continue

    if 'text' in row:
        tweet = clean(row['text'])
    else:
        tweet = None
    
    if 'created_at' in row:
        created_at = row['created_at']
    else:
        created_at = None
    
    if 'text_hash' in row:
        tweet_hash = row['text_hash']
    else:
        tweet_hash = None
    
    if 'collected_at' in row:
        collected_at = row['collected_at']
    else:
        collected_at = None
    
    if 'collection_type' in row:
        collection_type = row['collection_type']
    else:
        collection_type = None
        
    if 'lang' in row:
        lang = row['lang']
    else:
        lang = None
    
    place = row['place']
    if place == None:
        place_name = None
        country_code = None
    else:
        if 'full_name' in place:
            place_name = place['full_name']
        else:
            place_name = None
        
        if 'country_code' in place:
            country_code = place['country_code']
        else:
            country_code = None
    
    if 'province' in row:
        cronjob_tag = row['province']
    else:
        cronjob_tag = None
        
    user = row['user']
    if user == None:
        user_id = None
        user_name = None
        user_geoenabled = None
        user_lang = None
        user_location = None
        user_timezone = None
        user_verified = None
    else:
        if 'id_str' in user:
            user_id = user['id_str']
        else:
            user_id = None
        
        if 'screen_name' in user:
            user_name = user['screen_name']
        else:
            user_name = None
        
        if 'geo_enabled' in user:
            user_geoenabled = user['geo_enabled']
        else:
            user_geoenabled = None
        
        if 'lang' in user:
            user_lang = user['lang']
        else:
            user_lang = None
        
        if 'location' in user:
            user_location = clean(user['location'])
        else:
            user_location = None
        
        if 'time_zone' in user:
            user_timezone = user['time_zone']
        else:
            user_timezone = None
        
        if 'verified' in user:
            user_verified = user['verified']
        else:
            user_verified = None
    
    coordinates = row['coordinates']
    if coordinates == None:
        longitude = None
        latitude  = None
    else:
        if 'coordinates' in coordinates and len(coordinates['coordinates']) >= 2:
            longitude = coordinates['coordinates'][0]
            latitude  = coordinates['coordinates'][1]
        else:
            longitude = None
            latitude  = None
    
    cursor.execute("INSERT INTO tweets(id,tweet,tweet_hash,longitude,latitude,created_at,collected_at,collection_type,lang,place_name,country_code,cronjob_tag,user_id,user_name,user_geoenabled,user_lang,user_location,user_timezone,user_verified) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (id,tweet,tweet_hash,longitude,latitude,created_at,collected_at,collection_type,lang,place_name,country_code,cronjob_tag,user_id,user_name,user_geoenabled,user_lang,user_location,user_timezone,user_verified))
    
    mariadb_connection.commit()
    
mariadb_connection.close()