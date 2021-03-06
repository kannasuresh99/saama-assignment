FROM python:3.8-slim-buster

RUN apt-get update && apt-get -y install gcc
# By default, listen on port 5000
EXPOSE 5000/tcp
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY app.py .
COPY templates /app/templates

# Specify the command to run on container start
CMD [ "python", "./app.py" ]