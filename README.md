# Dockerized pipeline to analyse sentiment of tweets and post them to a Slack channel

## General info
Automated sentiment analysis of tweets of a Twitter user. The programm will get the latest tweets of the user, save them in a mongodb, analyze the sentiment of each tweet, save them in a postgresdb and finally post the tweet with the most negative and the tweet with the most positive sentiment to slack via a slackbot. Each of this processes is realized in a docker container.

## Technologies
* Python 3.9.7
* Docker 

## Setup
1. In the stream_tweets.py file add your Twitter credentials


2. In the post_tweet.py file add your slack webhook_url:
```
10 webhook_url = "<webhook_url>"
```

3. To create all docker images, go to the directory containing the compose.yml file and run in your terminal:
```
$ docker-compose build
```

5. Finall, to start all docker containers run in the terminal:
```
$ docker-compose up -d
```
