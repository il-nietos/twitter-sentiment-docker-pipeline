
'''
This script retrieves the most recent tweet from postgres and posts it to slack channel through a slack webhook.
'''
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import requests
import credentials 
import time

time.sleep(5) 

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


# Create a Webhook object to connect to SLACK
webhook_url =  credentials.WEBHOOK_SLACK 

# The query to get the worse score tweet
query_worst = f"""
    SELECT tweet, score
    FROM tweet_table
    ORDER BY score LIMIT 1
    """
# The query to get the best score tweet 
query_best = f"""
    SELECT tweet, score
    FROM tweet_table
    ORDER BY score DESC LIMIT 1
    """

while True:
    time.sleep(10)
    # reading query and write to variable with pandas:
    tweet_worst = pd.read_sql_query(query_worst, con=engine)
    tweet_best = pd.read_sql_query(query_best, con=engine)


    # get value of text and sentiment
    text_tweet_best = tweet_best['tweet'].iloc[0]
    sentiment_tweet_best =  tweet_best['score'].iloc[0]
        
    text_tweet_worst = tweet_worst['tweet'].iloc[0]
    sentiment_tweet_worst =  tweet_worst['score'].iloc[0]


# Create the JSON data object
    data = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*The most positive tweet*\n:white_check_mark: With a Score of {sentiment_tweet_best}\n{text_tweet_best}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*The most negative tweet*\n:x: With a Score of {sentiment_tweet_worst}\n{text_tweet_worst}"
                }
            }
        ]
    }



    # Post the data to the Slack
    #requests.post(url=webhook_url, json = data)
    print(data["blocks"][0]["text"]["text"])