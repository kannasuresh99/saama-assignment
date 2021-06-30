from datetime import date
from logging import debug
import re
from typing import List
from flask import Flask, redirect, url_for
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import requests
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "supersekrit"
screen_name = ()

#SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/twitter'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#database model
class User(db.Model):
    screen_name = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), unique=False)
    date = db.Column(db.Date, unique=False)

    def __init__(self, screen_name, text, date):
        self.screen_name = screen_name
        self.text = text
        self.date = date




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
#user_info = User(response['screen_name'])

@app.route("/tweets")
def tweets():
    index()
    screen_name = index.screen_name
    user_id = getUserid(screen_name)['data'][0]['id']
    res = getTimelineTweets(user_id)
    return res
    
    

if __name__ == "__main__":
    app.run(debug = True)