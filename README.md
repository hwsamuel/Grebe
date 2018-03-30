# Get the Web App Running in 5 Steps

1. Make sure you have [Python](https://www.python.org/downloads/) and [MariaDB](https://mariadb.com/downloads) installed (run the SQL commands in `schema.sql`)
2. Install [Flask](http://flask.pocoo.org/) by using `pip install flask` and the HTTP Auth dependency via `pip install flask-httpauth` 
3. Install Python MySQL Connector by using `pip install mysql-connector-python-rf`
4. In a terminal, use the command `python gserver.py` to run the Flask server
5. In your web browser, go to [http://127.0.0.1:5000/grebe/](http://127.0.0.1:5000/grebe/)

# Additional Dependencies

1. Install [Tweepy](http://www.tweepy.org) via `pip install tweepy`
2. Install PyMongo via `pip install pymongo`
3. Install the MySQL Connector `pip install mysql-connector`

# Aggregating Twitter Data in 5 Steps

1. Make sure you have [Python](https://www.python.org/downloads/) and [MariaDB](https://mariadb.com/downloads) installed (run the SQL commands in `schema.sql`)
2. Set up your [Twitter API keys](http://iag.me/socialmedia/how-to-create-a-twitter-app-in-8-easy-steps/)
3. Edit `authkey.py` and enter your API keys (each province can have a separate set of keys or all can use the same).
4. In a terminal, use the following command to run the aggregator `python gaggregate.py [stream | search] [ON | QC | NS | NB | MB | BC | PE | SK | AB | NL]`
5. If you want to aggregate data automatically, set up instances of the command above to run at scheduled intervals, for example as a cron job
