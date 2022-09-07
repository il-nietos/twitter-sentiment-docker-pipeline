# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
# (a text files with all the libraries you want to install)
# equivalent to "cp /local/path/requirement.txt /container/path/app"
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
# equivalent to being in the container terminal and running "pip install -r requirements.txt"
RUN pip install -r requirements.txt

CMD ["python", "stream_tweets.py"]