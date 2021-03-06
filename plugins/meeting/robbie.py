from slackclient import SlackClient
import yaml
import json
import logging
import sys

from helper import StandUpQueue

# Seconds to wait for person to give a report after called
PERSON_TIMEOUT = 1*60
# Seconds to wait before calling next person
WAIT_TO_CALL_NEXT = 1*60
# Seconds to wait before accomplishing a person after his report
WAIT_TO_ACCOMPLISH = 10
# Seconds to wait between greeting the channel and calling the first person
# In fact this means we'll effectively wait WAIT_BEFORE_START + WAIT_TO_CALL_NEXT
# seconds before starting to call people
WAIT_BEFORE_START = 1.5*60

# Load rtmbot configuration
config = yaml.load(file('rtmbot.conf', 'r'))
sc = SlackClient(config["SLACK_TOKEN"])

DEV = config["DEV"]

# Default rtmbot lists for sending messages and to periodically execute code
crontable = []
outputs = []
exit = False

# This is Robbie's ID
BOT_ID = 'U0BDUEDC4'
STAND_UP_CHANNEL = 'C04KCMH41' # #daily-stand-up

if DEV:
    channel_id = 'G0BDSLJSG' # bogus channel
    WAIT_BEFORE_START = 5
    WAIT_TO_CALL_NEXT = 5
else:
    channel_id = STAND_UP_CHANNEL

# Create a StandUpQueue object
attendants = StandUpQueue(wait_to_accomplish=WAIT_TO_ACCOMPLISH,
                          wait_before_start=WAIT_BEFORE_START,
                          wait_to_call_next=WAIT_TO_CALL_NEXT,
                          person_timeout=PERSON_TIMEOUT,
                          channel_id=channel_id,
                          outputs=outputs)

# Add our check to crontable. It's responsible for the timed actions
crontable.append([5,"check"])
def check():
    global attendants, exit
    attendants.check_timeout()
    attendants.call_next()
    # See if the meeting is finished. In this case rtmbot will know it should
    # stop running
    exit = attendants.finished

logging.info('Now we process')
def process_message(data):
    """ Main function responsible for handling all data from Slack channel. """
    global attendants
    try:
        # Print data
        print 'Incoming data: %s' % data

        # If we are developing, don't send data to STAND_UP_CHANNEL
        if DEV and data['channel'] == STAND_UP_CHANNEL:
            return

        # If he receives request from another channel, ignore it
        if data['channel'] != attendants.channel_id:
            return

        # Just return if attendants are finished
        if attendants.finished:
            return

        # Get user data from Slack API
        req =  sc.api_call("users.info", user=data['user'])
        user = json.loads(req)['user']

        # Ignore inputs from Robbie itself
        if user['name'] == 'robbie':
            return

        # Handle robbie interaction with users
        if '<@%s>' % BOT_ID in data['text']:
            attendants.handle_message(user, data)

        # Add user to attendants set
        if user['name'] != 'david': # Don't add david
            attendants.add(user, data['text'])
    except Exception:
        logging.exception('Problem processing message!')
