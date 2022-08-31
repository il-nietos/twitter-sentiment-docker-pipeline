'''This script 
'''

import credentials
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import MetaData, Column, String, DateTime, Integer, create_engine, Text, Numeric
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
import time
import pymongo
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#---------------------------------------#

# Steps
# 1. Extract: Retrieve tweets from MongoDB
# 2. Transform: Clean text with regex and analyse sentiment 
# 3. Load: Store tweets and sentiment score in Postgres

#---------------------------------------#
# 1. Retrieve tweets from MongoDB

# Connect to mongogb
#client = pymongo.MongoClient(host="mongodb", port=27017)
client = pymongo.MongoClient(host= 'localhost', port=27017)

time.sleep(10)  # seconds

# Select database
db = client.tweet_db

# Query tweets from MongoDB
def extract_tweets():
    docs = db.tweet_collection.find()
    return docs

#---------------------------------------#
# 2. Clean text with regex and analyse sentiment

mentions= '@[A-Za-z0-9_]+'
#url ='https?:\/\/\S+' #this will not catch all possible URLs
url = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
hashtag= '#'
retweet= 'RT\s'
numbers = '[\d]+'
dates = '(?:\d{2})*[ |,](?:Jan|Feb|Mar|oct)[a-z]*[ |,](?:\d{2},)*\d{4}'

# Clean text with regex and analyse sentiment
def clean_tweets(tweet):
    tweet = re.sub(mentions, '', tweet)  #removes @mentions
    tweet = re.sub(hashtag, '', tweet) #removes hashtag symbol
    tweet = re.sub(retweet, '', tweet) #removes RT to announce retweet
    tweet = re.sub(url, '', tweet) #removes most URLs
    tweet = re.sub(numbers, '', tweet) #removes most URLs
    tweet = re.sub(dates, '', tweet) #removes most URLs
    return tweet

# Transform: Clean text with regex and analyse sentiment
def transform_tweets(tweet):
    tweet = clean_tweets(tweet)
    analyser = SentimentIntensityAnalyzer()
    score = analyser.polarity_scores(tweet)['compound']
    return tweet, score

#---------------------------------------#

# 3. Store tweets and sentiment score in Postgres

# Get postgres credentials for postgres from credentials.py
host = credentials.host
port = credentials.port
user = credentials.user
dbname = credentials.dbname
psw = credentials.psw

# Create engine
engine = create_engine(f'postgresql://{user}:{psw}@{host}:{port}/{dbname}', echo=True)
if not database_exists(engine.url):
    create_database(engine.url)

# an instance of the sessionmaker()
Session = sessionmaker()
# create a session object

local_session= Session(bind=engine) 
Base = declarative_base()
metadata = MetaData()

# Define table
class Tweets(Base): # class Tweets inherits from base class

    __tablename__='tweet_table' #name of the table in the database
    
    id=Column('id', Integer, primary_key=True)
    tweet=Column('tweet', Text)
    score=Column('score', Numeric)
    date_created=Column(DateTime(), default=datetime.utcnow)
    
    def __repr__(self): # Dunder method for returning a nice string representation of the object
	    return f'<tweet ={self.tweet} score={self.score}'


Base.metadata.drop_all(bind=engine)
# Create the table if not exists 
Base.metadata.create_all(bind=engine, checkfirst=True) 

# def insert to postgres as separate function

def load_tweets(tweet, score):
    local_session.add(Tweets(tweet=tweet, score=score))
    local_session.commit()
    local_session.close()

for doc in docs:
   # print('============doc===============:', doc)
    text, score = transform_tweets(doc['tweet'])
    # score = analyser.polarity_scores(text)['compound']  
    new_tweet=Tweets(tweet=text, score=score, date_created=datetime.utcnow())
    local_session.add(new_tweet)
    time.sleep(1)
    local_session.commit()




