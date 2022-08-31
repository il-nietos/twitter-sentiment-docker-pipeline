''' This script gets tweets from twitter using twitter API and stores them in a mongodb database.'''
#---------------------------------------#
# Import packages

import credentials
import tweepy
import pymongo

#---------------------------------------#
# Create pymongo connection
client = pymongo.MongoClient(host= 'localhost', port=27017)

# Create database
db = client.tweet_db

# Create mongodb collection
collection = db.tweet_collection


#---------------------------------------#
# Connect to twitter API
client = tweepy.Client(
    bearer_token=credentials.bearer_token,
    wait_on_rate_limit=True
    )

#Looking for tweets about bitcoin, crypto and which are not retweets
#-has:media -- does not contain media
query = 'from:slatesartcodex crypto OR bitcoin -is:retweet'

#---------------------------------------#
# Retrieve tweets

# Define what user to get tweets from 
response = client.get_user(
    username='slatestarcodex',
    user_fields=['created_at', 'description', 'location',
                 'public_metrics', 'profile_image_url']
)

user = response.data

cursor = tweepy.Paginator(
    method=client.get_users_tweets,
    id=user.id,
    exclude=['replies', 'retweets'],
    tweet_fields=['author_id', 'created_at', 'public_metrics']
).flatten(limit=10)

# Store in mongodb
for tweet in cursor:
    tweet_new = {'tweet': tweet.text}
    collection.insert_one(tweet_new)

# Execute this script when run directly
if __name__ == '__main__':
    while True:
        stream_tweets(5, warning_log)
        time.sleep(30)