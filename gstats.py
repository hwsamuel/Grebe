from province import Province, Provinces
import mysql.connector as mariadb

mariadb_connection = mariadb.connect(user='root', password='', database='grebe')
cursor = mariadb_connection.cursor(buffered=True)

def all_tweets():
    cursor.execute("SELECT Count(id) FROM tweets")
    return cursor.fetchone()[0]

def tweets_with_coordinates():
    cursor.execute("SELECT Count(id) FROM tweets WHERE latitude Is Not Null AND longitude Is Not Null")
    return cursor.fetchone()[0]

def tweets_in_province(province):
    cursor.execute("SELECT Count(id) FROM tweets WHERE latitude Is Not Null AND longitude Is Not Null AND place_name Like '%" + province.value.name + "'")
    return cursor.fetchone()[0]

def main():
    print 'Total Tweets: '+str(all_tweets())
    print 'Tweets with coordinates: '+str(tweets_with_coordinates())
    
    provinces = [Provinces.AB, Provinces.SK, Provinces.BC, Provinces.MB]
    for province in provinces:
        tweets = tweets_in_province(province)
        print 'Tweets from ' + province.value.name + ': ' + str(tweets)

if __name__ == "__main__":
    main()