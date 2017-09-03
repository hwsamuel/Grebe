from datetime import datetime
from province import Province, Provinces
import time, mysql.connector as mariadb

mariadb_connection = mariadb.connect(user='root', password='', database='grebe')
cursor = mariadb_connection.cursor(buffered=True)

EPOCH = '2016-07-14'

def get_tweets(start = None, end = None, keywords = None, fields = None, province = None, strict = True):
    if fields == None:
        fields = 'tweet, longitude, latitude, created_at, place_name, user_name'
    
    if start == None:
        start = datetime.strptime(EPOCH, '%Y-%m-%d')
    else:
        start = datetime.strptime(start, '%d-%m-%Y')
    
    if end == None:
        today = time.strftime("%Y-%m-%d")
        end = datetime.strptime(today, '%Y-%m-%d')
    else:
        end = datetime.strptime(end, '%d-%m-%Y')

    if end < start:
        raise Exception('The end date is before the start date')
    
    if strict:
        strict_filter = "longitude Is Not Null AND latitude Is Not Null AND country_code = 'CA' AND "
    else:
        strict_filter = ""
    qry = "SELECT " + fields + " FROM tweets WHERE " + strict_filter + " created_at >= '" + str(start) + "' AND created_at <= '" + str(end) + "'"
    
    if province:
        qry += " AND (place_name Like '%" + province.value.name + "')"
    
    if keywords:
        keywords = keywords.lower()
        st = "tweet Like '%"
        keywords = keywords.replace('|', "%' OR " + st)
        keywords = keywords.replace('+', "%' AND " + st)
        qry += " AND (" + st + keywords + "%')"
    
    cursor.execute(qry)
    return list(cursor)