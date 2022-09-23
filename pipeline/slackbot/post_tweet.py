'''This script retrieves the most recent tweet from postgres
and posts it to slack channel through a slack webhook.
'''
import time
import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import config

time.sleep(5)

# Create engine

engine = create_engine('postgresql://docker_user:1234@postgresdb:5432/twitter', echo=False)
if not database_exists(engine.url):
    create_database(engine.url)


# Create a Webhook object to connect to SLACK
WEBHOOK_SLACK =  config.WEBHOOK_SLACK

# The query to get the best score tweet
query = '''
    SELECT text, score, posted, like_count
    FROM tweet_table
    ORDER BY tweet_timestamp ASC LIMIT 1
    '''

while True:
    time.sleep(10)
    # reading query and write to variable with pandas:
    tweet = pd.read_sql_query(query, con=engine)

    # get value of text and sentiment
    text_tweet = tweet['text'].iloc[0]
    sentiment_tweet =  tweet['score'].iloc[0]
    like_count_tweet = tweet['like_count'].iloc[0]


# Create JSON data object

    data = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text":
                        f'''*Just tweeted*\n:white_check_mark:
                        With a Score of {sentiment_tweet}\n{text_tweet}\n{like_count_tweet} users liked this tweet.'''
                    }
                }
            ]
        }

    # Post the data to the Slack
    requests.post(url=WEBHOOK_SLACK, json = data, timeout=30)
    
