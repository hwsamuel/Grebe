import mysql.connector as mariadb, sys

sys.path.append('../')
from config import *

mariadb_connection = mariadb.connect(user=DB_USER, password=DB_PWD, database=DB_NAME)
cursor = mariadb_connection.cursor()

def all_tweets():
    cursor.execute("SELECT Count(id) FROM tweets")
    return cursor.fetchone()[0]

def tweets_with_coordinates():
    cursor.execute("SELECT Count(id) FROM tweets WHERE latitude Is Not Null AND longitude Is Not Null")
    return cursor.fetchone()[0]

def tweets_in_province(province):
    cursor.execute("SELECT Count(id) FROM tweets WHERE latitude Is Not Null AND longitude Is Not Null AND place_name Like '%" + province + "'")
    return cursor.fetchone()[0]

def main():
    print 'Total Tweets: '+str(all_tweets())
    print 'Tweets with coordinates: '+str(tweets_with_coordinates())
    
    for province in CANADA_PROVINCES:
        tweets = tweets_in_province(province)
        print 'Tweets from ' + province + ': ' + str(tweets)

if __name__ == "__main__":
    main()