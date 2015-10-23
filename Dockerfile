FROM ubuntu:14.04

MAINTAINER Allan Costa "allan@cloudwalk.io"

RUN apt-get update && \
    apt-get install -y python-pip

WORKDIR /src/rtmbot
COPY . /src/rtmbot

RUN pip install -r requirements.txt

ENV DEV 'False'

# Create a startup.sh bash script to create a rtmbot.conf with SLACK_TOKEN before running the bot
RUN echo '#!/bin/bash\n echo "DEBUG: False \nDEV: $DEV \nSLACK_TOKEN: $SLACK_TOKEN" >> /src/rtmbot/rtmbot.conf  \nexec /src/rtmbot/rtmbot.py' >> startup.sh && \
    chmod +x startup.sh

ENTRYPOINT ["/src/rtmbot/startup.sh"]
