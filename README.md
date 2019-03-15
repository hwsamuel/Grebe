## Grebe Social Data Aggregator

Grebe aggregates geo-fenced Canadian Twitter data for research in sociology and public health. View our [__demo__](http://199.116.235.207/grebe) to see how the data collected by Grebe can be analyzed and visualized in various ways. The demo is IaaS-hosted thanks to [Cybera](http://www.cybera.ca). This project is supported by the [Alberta Machine Intelligence Institute (Amii)](http://amii.ca).
 
## Get the Web App Running

1. Install [Python](https://www.python.org/downloads)
2. Install [Flask](http://flask.pocoo.org/) by using `pip install flask`
3. Install Flash's HTTP Auth dependency via `pip install flask-httpauth`
4. Install [MariaDB](https://mariadb.com/downloads) and edit `spyder.py`, `gexport.py`, `gserver.py`, `gstats.py` to enter your database username and password 
5. Run the SQL commands in `schema.sql` to set up a database
6. Install [TwitterAPI](https://github.com/geduldig/TwitterAPI) via `pip install TwitterAPI`
7. Install the MySQL Connector via `pip install mysql-connector`
8. Install Python MySQL Connector by using `pip install mysql-connector-python-rf` 
9. In a terminal, use the command `python gserver.py` to run the Flask server
10. In your web browser, go to [http://127.0.0.1:5000/grebe/](http://127.0.0.1:5000/grebe/)

## Aggregating Twitter Data

1. Sign up for a [Twitter Developer](http://developer.twitter.com/) account
2. Set up your [Twitter API keys](http://iag.me/socialmedia/how-to-create-a-twitter-app-in-8-easy-steps/)
3. Edit `spyder.py` and enter your API keys
4. In a terminal, use the following command to run the aggregator `python spyder.py [status | search | stream]`
5. If you want to aggregate data automatically, set up instances of the command above to run at scheduled intervals, for example as a cron job