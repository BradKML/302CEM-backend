import tweepy
import unittest
import pymysql
from flask import Flask, jsonify, request 
import flask

# setting the api
def Test_start_api(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

# API keys in question
ck="DxHoukAprUS9cgUXR4yLPfy5n"
cs="2s1fiLCR4QGdlBVkDPh0WQgGOWA6rmcFIE5wzY5nYa1AsSayn2"
at="1207894049106956288-vVSh9pHeHm0GRKRXTNxnVVM9Ep1aiD"
ats="FY40u4cNBixTBzl5n9lH4847IGz5vCbHSBbYH9BNrK2g1"
my_api = Test_start_api(ck,cs,at,ats)

app = Flask(__name__)

name = "AgileTest8"

# basic data fetch function
def Test_get_api_info(name):
    user = my_api.get_user(screen_name = name)
    return [user.name,user.created_at.strftime('%Y-%m-%d'),user.followers_count,user.friends_count,user.statuses_count,user.favourites_count]

user, cre, followers, following, tweet, like = Test_get_api_info(name)

class TestApi(unittest.TestCase):

    def test_api_name(self):
        self.assertTrue(user == "Agile Test")
        
    def test_api_date(self):
        self.assertTrue(cre == "2019-12-31")

    def test_followers(self):
        self.assertTrue(followers == 0)

    def test_following(self):
        self.assertTrue(following == 6)

    def test_tweet(self):
        self.assertTrue(tweet == 0)

    def test_like(self):
        self.assertTrue(like == 3)
    

if __name__ == '__main__':
    unittest.main()
