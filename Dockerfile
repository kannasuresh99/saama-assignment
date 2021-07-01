# Set base image (host OS)
FROM python:3.8-slim-buster

RUN apt-get update && apt-get -y install gcc
# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY app.py .
ADD templates/tweets.html .
ADD templates/tweets_filter.html .

# Specify the command to run on container start
CMD [ "python", "./app.py" ]