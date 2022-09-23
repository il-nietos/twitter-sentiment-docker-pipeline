# Dockerized ETL-pipeline for tweet sentiment analysis

## Description

Automated sentiment analysis of tweets of a chosen user. The programm, run by Docker compose will:

1. Stream incoming tweets with the help of twitter API
2. Store tweets in MongoDB
3. ETL: 
* Extract tweets from MongoDB
* Transform: clean and analyse the sentiment with VaderSentiment
* Load tweets and sentiment score in PostgreSQL

4. Post the tweet to a slack channel using a slackbot

## Technologies

* Python 3.9
* Docker 
* MongoDB
* pymongo
* PostgreSQL
* SQLAlchemy
* VaderSentiment

## Setup

(Install Docker: https://docs.docker.com/get-docker/)


1. Clone this repository: git clone [https://github.com/il-nietos/twitter-sentiment-docker-pipeline.git]

2. Install packages in a conda environment 
$ conda install --name <environment_name> --file requirements.txt


3. Add your Twitter and Slack credentials to the config_example.py and rename to config.py

4. In the post_tweet.py file add your slack webhook_url:
```
 webhook_url = "<webhook_url>"
```

5. To start running the docker compose and begin streaming tweets, go to the directory containing the compose.yml file and run in your terminal:
```
$ docker-compose build && docker-compose up
```
