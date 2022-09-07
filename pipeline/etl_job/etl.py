'''This script retrieves the tweets from mongodb, cleans them,
analyses the sentiment of the tweets and stores the tweet and
the sentiment score in postgreSQL database.
'''

import re
import time
from datetime import datetime
import pymongo
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import MetaData, Column, DateTime, Integer, create_engine, String, Numeric
from sqlalchemy_utils import database_exists, create_database
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import config
#---------------------------------------#

# Steps
# 1. Extract: Retrieve tweets from MongoDB
# 2. Transform: Clean text with regex and analyse sentiment
# 3. Load: Store tweets and sentiment score in Postgres

#---------------------------------------#
# 1. Retrieve tweets from MongoDB

# Connect to mongogb
#client = pymongo.MongoClient(host="mongodb", port=27017)
client = pymongo.MongoClient(host='mongodb', port=27017)

time.sleep(10)  # seconds

# Select database
# db = client.tweet_db
db = client.crypto_db


# Create engine
engine = create_engine('postgresql://docker_user:1234@postgresdb:5432/twitter', echo=True)
if not database_exists(engine.url):
    create_database(engine.url)


# Query tweets from MongoDB
def extract_tweets():
    ''''Returns a list of tweets from mongodb'''
    # docs = db.tweet_collection.find()
    documents = db.crypto_collection.find()
    return documents

docs = extract_tweets()

#---------------------------------------#
# 2. Clean text with regex and analyse sentiment

MENTIONS= '@[A-Za-z0-9_]+'
#url ='https?:\/\/\S+' #this will not catch all possible URLs
# url = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
HASHTAG= '#'
#RETWEET= 'RT\s'
# numbers = '[\d]+'
DATES = '(?:\d{2})*[ |,](?:Jan|Feb|Mar|oct)[a-z]*[ |,](?:\d{2},)*\d{4}'


def clean_tweets(tweet):
    '''Removes mentions, hashtags, urls, retweets and numbers from tweet text.
    Returns a clean text'''
    tweet = re.sub(MENTIONS, '', tweet)  #removes @mentions
    tweet = re.sub(HASHTAG, '', tweet) #removes hashtag symbol
    #tweet = re.sub(RETWEET, '', tweet) #removes RT to announce retweet
    # tweet = re.sub(url, '', tweet) #removes most URLs
    # tweet = re.sub(numbers, '', tweet) #removes most URLs
    tweet = re.sub(DATES, '', tweet) #removes most URLs
    return tweet


def transform_tweets(tweet):
    '''Calls the clean_tweets function and analyses the returned clean text.
    Returns text and sentiment score'''
    clean_text = clean_tweets(tweet)
    analyser = SentimentIntensityAnalyzer()
    sentiment_score = analyser.polarity_scores(clean_text)['compound']
    return clean_text, sentiment_score

#---------------------------------------#
# 3. Store tweets and sentiment score in Postgres

# an instance of the sessionmaker()
Session = sessionmaker()

# create a session object
local_session= Session(bind=engine)

Base = declarative_base()
metadata = MetaData()

# Define table
class Tweets(Base): # class Tweets inherits from base class
    '''Defines the table and the columns in postgreSQL.'''
    __tablename__='tweet_table' #name of the table in the database

    id=Column('id', Integer, primary_key=True)
    text=Column('text', String)
    score=Column('score', Numeric)
    like_count=Column('like_count', Integer)
    tweet_timestamp=Column('tweet_timestamp', DateTime())
    date_created=Column(DateTime(), default=datetime.utcnow)
    posted=Column('posted', Integer, default=0)

    def __repr__(self): # Dunder method for returning a nice string representation of the object
        '''Returns a nice string representation of the object'''
        return f'<text ={self.text} score={self.score}'


# Clear the table
Base.metadata.drop_all(bind=engine)
# Create the table if not exists
Base.metadata.create_all(bind=engine, checkfirst=True)

# def insert to postgres as separate function
def load_tweets(text, score):
    '''Inserts tweets and sentiment score into postgres database'''
    local_session.add(Tweets(text=text, score=score))
    local_session.commit()
    local_session.close()


for doc in docs:
   # print('============doc===============:', doc)
    text, score = transform_tweets(doc['text'])
    like_count = doc['like_count']
    tweet_timestamp = doc['timestamp']
    # score = analyser.polarity_scores(text)['compound']
    new_tweet=Tweets(
        text=text,
        score=score,
        like_count=like_count,
        tweet_timestamp = tweet_timestamp)
       # date_created=datetime.utcnow())
    local_session.add(new_tweet)
    time.sleep(1)
    local_session.commit()

