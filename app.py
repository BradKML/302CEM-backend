# using flask_restful 
import tweepy
import pymysql
from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api 
import datetime
from datetime import date
import flask

#setting the api
def start_api(consumer_key, consumer_secret,
  access_token, access_token_secret):

  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)  
  auth.set_access_token(access_token, access_token_secret)  
  return tweepy.API(auth)

# API keys in question
ck="DxHoukAprUS9cgUXR4yLPfy5n"
cs="2s1fiLCR4QGdlBVkDPh0WQgGOWA6rmcFIE5wzY5nYa1AsSayn2"
at="1207894049106956288-vVSh9pHeHm0GRKRXTNxnVVM9Ep1aiD"
ats="FY40u4cNBixTBzl5n9lH4847IGz5vCbHSBbYH9BNrK2g1"
my_api = start_api(ck,cs,at,ats)

# creating the flask app 
app = Flask(__name__) 

def get_user_info(name):
  user = my_api.get_user(screen_name = name) 
  return {"username": user.name,
            "creation date": user.created_at.strftime('%Y-%m-%d'),
            "followers count": user.followers_count,
            "following count": user.friends_count,
            "tweet count": user.statuses_count,
            "like count": user.favourites_count}

#insert the data in the mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:P@ssw0rd123@127.0.0.1/twitter'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Account_created(db.Model): # create table Account_created
    __tablename__ = 'Account_created'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50))
    created_at = db.Column('created_at', db.DateTime)

    def __init__(self, username, created_at):
        self.username = username
        self.created_at = created_at

class Twitter(db.Model): # create table twitter
    __tablename__ = 'Twitter'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50))
    DATE = db.Column('DATE', db.Date)
    followers_count = db.Column('followers_count', db.Integer)
    following_count = db.Column('following_count', db.Integer)
    tweet_count = db.Column('tweet_count', db.Integer)
    like_count = db.Column('like_count', db.Integer)

    def __init__(self, username, DATE, followers_count, following_count, tweet_count, like_count):
        self.username = username
        self.DATE = DATE
        self.followers_count = followers_count
        self.following_count = following_count
        self.tweet_count = tweet_count
        self.like_count = like_count
        
def insert_data(name):
  # this line is for actualy getting data from the API
  info = get_user_info(name)#get_api_info
  # try to separate the value that the api returns, but can't get them when i was using app.route, so that i can insert it into mysql database
  today = date.today()
  exists = db.session.query(Account_created.id).filter_by(username=info["username"]).scalar() is not None # exists tests if the user exists in the database or not
  dateexist = db.session.query(Twitter.id).filter_by(DATE = today, username = info["username"]).scalar() is not None # dateexist tests if the current datapoint exitss in the database or not
  #print (exists);
  #print(dateexist);

  if(exists == False):# create new information
    
    data = Account_created(info["username"],info["creation date"])
    db.session.add(data)
    db.session.commit()
    # the next three lines are used to add data into the database
    insdata = Twitter(info["username"],today.strftime('%Y-%m-%d'),info["followers count"],info["following count"],info["tweet count"],info["like count"])
    db.session.add(insdata)
    db.session.commit()
    
  elif(dateexist == False):#add a new day data
   insdata = Twitter(info["username"],today.strftime('%Y-%m-%d'),info["followers count"],info["following count"],info["tweet count"],info["like count"])
   db.session.add(insdata)
   db.session.commit()
  
  elif(dateexist == True):#update query when there has changes in that day data
   updatedata = Twitter.query.filter_by(username = info["username"], DATE = today).update({"followers_count": (info["followers count"]), "following_count": (info["following count"]),"tweet_count": (info["tweet count"]), "like_count": (info["like count"])})
   db.session.commit()
    
  # the followine line is used to get data from the database
  r = db.engine.execute('select username,DATE,followers_count,following_count,tweet_count,like_count from Twitter where username = "' + info["username"] + '" ORDER BY DATE DESC')
  
  # in here, x, y and z are the partial return values
  x = [{"date":i[1].strftime('%Y-%m-%d'),"followers":i[2],"following":i[3],"tweets":i[4]} for i in r] #just loop 
  
  y = [{"followers_diff":x[i]["followers"]-x[i+1]["followers"],
        "following_diff":x[i]["following"]-x[i+1]["following"],
        "tweets_diff":x[i]["tweets"]-x[i+1]["tweets"]}
        for i in range(len(x)-1)] + [{"followers_diff":0,"following_diff":0,"tweets_diff":0}]
  
  z = [{**x[i], **y[i]} for i in range(len(x))]
  # finally we are returning the data to the API
  return (flask.jsonify({"name": info["username"], "cre": info["creation date"],"like": info["like count"], "table": z}))

# make a new function here with a decorator implies an internal variable called "name"
@app.route('/<name>')
def flask_json(name):
    return insert_data(name)

if __name__ == '__main__':
    app.run(debug=True)
