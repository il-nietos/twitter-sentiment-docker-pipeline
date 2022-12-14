'''
This script gets tweets from twitter using twitter API and stores them in a mongodb database.
'''
import json
import time
import tweepy
import pymongo
import config

# Create pymongo connection and a collection within mongodb
def create_collection():
    '''Connects to mongodb and create a collection to store tweets.'''

    client = pymongo.MongoClient(host='mongodb')  # hostname = servicename for docker-compose pipeline
    # Create mongodb collection
    collection = client.crypto_db.crypto_collection
    x = collection.delete_many({})
    print(x.deleted_count, "documents deleted")
    return collection

# Authenticate access config to twitter API
def authenticate():
    """Function for handling Twitter Authentication, add here your own keys.
    config.py stores the following keys:
       1. API_KEY
       2. API_SECRET
       3. ACCESS_TOKEN
       4. ACCESS_TOKEN_SECRET
    """
    auth = tweepy.OAuth1UserHandler(
    config.API_KEY, # replace this with your own key
    config.API_KEY_SECRET, # replace this with your own key
    config.ACCESS_TOKEN, # replace this with your own key
    config.ACCESS_TOKEN_SECRET) # replace this with your own key
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

# Create Streamer class that connects to twitter api and
# streams tweets in real time and stores them in mongodb
class Streamer(tweepy.StreamingClient): # Streamer class inherits from tweepy.StreamingClient class
    '''Define streamer class. An instance of this class
    1. connects to the Twitter Streaming API
    2. Collects tweets
    3. stores them in mongodb in JSON formt'''

    new_tweet = {} # a dictionary to store incoming tweets

    def on_connect(self):
        print('Connected to Twitter Streaming API') # prints once tweets begin to stream

    def on_data(self, data): # data received from the stream is passed to this method
        '''Method called when new data arrives from the stream.
        Converts the data to json format and stores it in mongodb'''

        full = json.loads(data) # convert data to json format
        tweet_data = full['data']
        #try:
        #    if tweet_data['referenced_tweets'] is None: # filters out retweets
        #        pass
        #except:
        self.new_tweet = {
        'text': tweet_data['text'],
        'id': tweet_data['id'],
        'like_count': tweet_data['public_metrics']['like_count'],
        'timestamp': tweet_data['created_at']
        }
        collection.insert_one(self.new_tweet) # insert each tweet into mongodb collection
        print('Tweet stored in the the collection:', self.new_tweet)
        time.sleep(30)

    def on_error(self, status):
        '''Disconnect stream when rate limit is reached'''
        if status == 429:
            print('Rate limit exceeded, wait for 15 minutes', status)
            time.sleep(60*15)


def initiate_stream_object():
    ''' Initiates the stream object'''
    stream = Streamer(bearer_token = config.BEARER_TOKEN) # replace this with your own key
    return stream

# Define three functions that: first get the current rules in place,
# delete them (to start with a blank slate,
# and then set new rules for streaming)
def get_rules():
    '''Returns current filtering rules set for streaming'''

    rules = stream.get_rules()
    if rules.data is not None:
        print(f"current rules: {rules.data}")
    else:
        print("no rules found")
    return rules


def delete_all_rules(rules, stream):
    '''Deletes all rules set for streaming'''
    rule_ids = []
    try:
        if rules.data is not None:
            for rule in rules.data:
                print(f"rule marked to delete: {rule.id} - {rule.value}")
                rule_ids.append(rule.id)
    except:
        print('No rules found')

    if len(rule_ids) > 0:
        stream.delete_rules(rule_ids)
    else:
        print("no rules to delete")

def set_rules():
    '''Sets rules for streaming'''
    search_terms = ['ethereum lang:en', 'bitcoin lang:en', 'crypto lang:en']
    for term in search_terms:
        stream.add_rules(tweepy.StreamRule(term))

# Start the stream, filter based on rules added
def get_stream():
    '''Starts streaming tweets'''
    stream.filter(
    tweet_fields=['referenced_tweets', 'author_id', 'created_at', 'public_metrics'],
    user_fields=['name', 'username'])

# Execute the script
if __name__ == '__main__':
    collection = create_collection()
    api = authenticate()
    stream = initiate_stream_object()
    rules = get_rules()
    delete_all_rules(rules, stream)
    set_rules()
    get_stream()
