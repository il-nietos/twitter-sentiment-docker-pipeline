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
* Python 3.9.7
* Docker 

## Setup

1. Install packages in a conda environment 
$ conda install --name <environment_name> --file requirements.txt


2. In the stream_tweets.py file add your Twitter credentials

3. In the post_tweet.py file add your slack webhook_url:
```
 webhook_url = "<webhook_url>"
```

4. To create all docker images, go to the directory containing the compose.yml file and run in your terminal:
```
$ docker-compose build
```

5. Finall, to start all docker containers run in the terminal:
```
$ docker-compose up -d
```
