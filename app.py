from flask import Flask, redirect, url_for, render_template, request
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists
from datetime import datetime
import time
import atexit


app = Flask(__name__)
app.secret_key = "supersekrit"
screen_name = ()

#SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/twitter?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), unique=False)
    date = db.Column(db.DateTime, unique=False)

    def __init__(self, id, text, date):
        self.id = id
        self.text = text
        self.date = date
    
    def __repr__(self):
        return '<User {}>'.format(self.id)




#twitter credentials to fetch data
blueprint = make_twitter_blueprint(
    api_key="YhDEfAPUu3w2tNeERoWbIsDG8",
    api_secret="DWsGDulYhk5BbOGUZ8N3Bxty67BROA7mqiLppsoqgIhO3lRu9K",
)
app.register_blueprint(blueprint, url_prefix="/login")

@app.route("/")
def index():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    account_info = twitter.get("account/settings.json")
    if account_info.ok:
        account_info_json = account_info.json()
        index.screen_name = account_info_json['screen_name']
        return redirect(url_for('tweets'))
    return "<h1>Login failed!</h1>"

#fetching user's twitter username_id using user's screen_name(twitter_id)
def getUserid(screen_name):
    url = "https://api.twitter.com/2/users/by?usernames={}&user.fields=created_at&expansions=pinned_tweet_id&tweet.fields=author_id,created_at".format(screen_name)
    payload={}
    headers = {
    'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAHylRAEAAAAAsJinLVRF93uKxY0pzSRo63PmMmg%3DQy2xFNQWVZxAyGjbYr094iZ7sZFg2UsFVVprzUuhTFFSqnUk1J',
    'Cookie': 'guest_id=v1%3A162498436179752708; personalization_id="v1_n0j0GC5abMP002A8A+gKTg=="'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    return response

#fetching the user's twitter line using twitter api and user's twitter unique username_id
def getTimelineTweets(user_id):
    url = "https://api.twitter.com/2/users/{}/tweets?tweet.fields=created_at&expansions=author_id&user.fields=created_at&max_results=30".format(user_id)

    payload={}
    headers = {
    'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAHylRAEAAAAAsJinLVRF93uKxY0pzSRo63PmMmg%3DQy2xFNQWVZxAyGjbYr094iZ7sZFg2UsFVVprzUuhTFFSqnUk1J'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    return response

#function to convert ISO datetime format to default datetime format
def getDateTime(date):
    created_at = datetime.strptime(date,"%Y-%m-%dT%H:%M:%S.000%z")
    created_at = str(created_at)
    created_at_date = created_at[:10]
    created_at_date = datetime.strptime(created_at_date, "%Y-%m-%d")
    return created_at_date

@app.route("/tweets")
def tweets():
    index()
    screen_name = index.screen_name
    user_id = getUserid(screen_name)['data'][0]['id']
    res = getTimelineTweets(user_id)
       
    db.create_all()
    for i in range(0,len(res['data'])):
        k = 0
        timeline_tweets = User(k ,res['data'][i]['text'], getDateTime(res["data"][i]['created_at']))
        db.session.add(timeline_tweets)
        db.session.commit()
        k += 1
    return render_template('tweets.html', users = User.query.all())

@app.route("/tweets_filtered_by_date",methods = ['POST', 'GET'])
def filterByDate():
    if request.method == 'POST':
      result = request.form
      for key, value in result.items():
          filtering_date = value
      return render_template('tweets_filter.html', users = User.query.filter(User.date.like('%{}%'.format(filtering_date))).all())

@app.route("/tweets_filtered_by_keyword",methods = ['POST', 'GET'])
def filterByKeyword():
    if request.method == 'POST':
      result = request.form
      for key, value in result.items():
          filtering_keyword = value
      return render_template('tweets_filter.html', users = User.query.filter(User.text.like('%{}%'.format(filtering_keyword))).all())

@app.route('/tweets_asc')
def tweetsAsc():
    return render_template('tweets_filter.html', users = User.query.order_by(User.date.asc()))

@app.route('/tweets_desc')
def tweetsDesc():
    return render_template('tweets_filter.html', users = User.query.order_by(User.date.desc()))

    

if __name__ == "__main__":
    app.run(debug = True)
