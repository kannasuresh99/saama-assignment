from flask import Flask, redirect, url_for, render_template, request
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_apscheduler import APScheduler


application = Flask(__name__)
application.secret_key = "supersekrit"
scheduler = APScheduler()

#SqlAlchemy Database Configuration With Mysql
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:12345678@database-2.c9d4vjz3jbqc.ap-south-1.rds.amazonaws.com:3306/twitter?charset=utf8mb4'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)

#database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.String(100), unique=True)
    text = db.Column(db.String(200), unique=True)
    date = db.Column(db.DateTime, unique=False)
    screen_name = db.Column(db.String(50), unique=False)

    def __init__(self, id, tweet_id, text, date, screen_name):
        self.id = id
        self.tweet_id = tweet_id
        self.text = text
        self.date = date
        self.screen_name = screen_name
    
    def __repr__(self):
        return '<User {}>'.format(self.id)




#twitter credentials to fetch data
blueprint = make_twitter_blueprint(
    api_key="YhDEfAPUu3w2tNeERoWbIsDG8",
    api_secret="DWsGDulYhk5BbOGUZ8N3Bxty67BROA7mqiLppsoqgIhO3lRu9K",
)
application.register_blueprint(blueprint, url_prefix="/login")

@application.route("/")
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



@application.route("/tweets")
def tweets():
    index()
    screen_name = index.screen_name
    user_id = getUserid(screen_name)['data'][0]['id']
    res = getTimelineTweets(user_id)
    db.create_all()
    if User.query.filter_by(screen_name=screen_name).first() is None:
        db.session.query(User).delete()
        for i in range(0,len(res['data'])):
            k = 0
            timeline_tweets = User(k , res['data'][i]['id'], res['data'][i]['text'], getDateTime(res["data"][i]['created_at']), screen_name)
            db.session.add(timeline_tweets)
            db.session.commit()
            k += 1
    return render_template('tweets.html', users = User.query.all())

@application.route("/tweets_filtered_by_date",methods = ['POST', 'GET'])
def filterByDate():
    if request.method == 'POST':
      result = request.form
      for key, value in result.items():
          filtering_date = value
      return render_template('tweets_filter.html', users = User.query.filter(User.date.like('%{}%'.format(filtering_date))).all())

@application.route("/tweets_filtered_by_keyword",methods = ['POST', 'GET'])
def filterByKeyword():
    if request.method == 'POST':
      result = request.form
      for key, value in result.items():
          filtering_keyword = value
      return render_template('tweets_filter.html', users = User.query.filter(User.text.like('%{}%'.format(filtering_keyword))).all())

@application.route('/tweets_asc')
def tweetsAsc():
    return render_template('tweets_filter.html', users = User.query.order_by(User.date.asc()))

@application.route('/tweets_desc')
def tweetsDesc():
    return render_template('tweets_filter.html', users = User.query.order_by(User.date.desc()))


if __name__ == "__main__":
    scheduler.add_job(id = 'Scheduled Task', func=tweets, trigger="interval", seconds=120)
    scheduler.start()
    application.run(host='0.0.0.0', port=5000)