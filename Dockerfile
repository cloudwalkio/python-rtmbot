FROM ubuntu:14.04

MAINTAINER Allan Costa "allan@cloudwalk.io"

RUN apt-get update && \
    apt-get install -y python-pip

WORKDIR /src/rtmbot
COPY . /src/rtmbot

RUN pip install -r requirements.txt

ENTRYPOINT ["/src/rtmbot/rtmbot.py"]
