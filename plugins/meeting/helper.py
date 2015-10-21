import time
import datetime
import random

CREATOR_NICKNAME = 'allanino'

def link(data, link_type='person'):
    """ Return a link to @person or #channel. """
    if link_type == 'channel':
        return '<#%s|%s>' % (data['id'], data['name'])
    else:
        return '<@%s|%s>' % (data['id'], data['name'])

def call(person, first=False):
    """ Return a message calling a person. The first flag is to use special
        messages for the first person being called on a meeting.
    """
    if first:
        responses = ["%s: let's ro//",
                     "%s: let's rock'n ro//",
                     "%s: let's get started!",
                     "%s: you're the firrrrssssttttt!"]
    elif person['name'] == CREATOR_NICKNAME:
        responses = ["Oh my great creator, %s, it's your turn!",
                     "Tell me, creator %s, what you've been doing?",
                     "I'm so excited! It's the master %s turn!"]
    else:
        responses = ["%s: next please",
                     "%s: next please",
                     "Hey %s, tell us what you have been up to!",
                     "%s: what about yourself?",
                     "%s: your turn",
                     "%s: your turn"]
    return random.choice(responses) % link(person)

def accomplish(person, wait_to_accomplish):
    """ Return a message accomplishing a person """
    # Wait some time, just to give an impression that Robbie is reading.
    time.sleep(wait_to_accomplish)

    if person['name'] == CREATOR_NICKNAME:
        responses = ['Nice work creator %s :thumbsup:',
                     'Thanks my creator %s :thumbsup:',
                     "You've been busy master %s, you deserve a break! Well done :thumbsup:",
                     "Not a bad day yesterday master %s, good job :thumbsup:",
                     "Is that all? Haha only joking, nice job creator %s :thumbsup:"]
    else:
        responses = ['Nice work %s :thumbsup:',
                     'Nice work %s :thumbsup:',
                     'Nice work %s :thumbsup:',
                     'Nice work %s :thumbsup:',
                     'Thanks %s :thumbsup:',
                     'Thanks %s :thumbsup:',
                     'Thanks %s :thumbsup:',
                     'Thanks %s :thumbsup:',
                     "You've been busy %s, you deserve a break! Well done :thumbsup:",
                     "Not a bad day yesterday %s, good job :thumbsup:",
                     "Is that all? Haha only joking, nice job %s :thumbsup:"]
    return random.choice(responses) % person['profile']['first_name']

def deny_request(person):
    responses = ["Hello %s! I like you, but I only accept orders from my masters.",
                 "I know you like to be heard %s, but please don't interrupt me when I am busy.",
                 "Keep trying %s, but it won't work :grin:",
                 "%s `secret code activation success` this meeting will self-destruct in 5-4-3-2...",
                 "%s you really must try harder than that."]
    return random.choice(responses) % link(person)

def talk(person, data):
    """ Here we should handle easy talk to Robbie. """
    responses = ['%s: :smiley:',
                 '%s: :smile:',
                 '%s: :godmode:',
                 '%s: :metal:',
                 '%s: :bowtie:',
                 '%s: :troll:',
                 '%s: :beer:']
    return random.choice(responses) % link(person)

def greeting():
    responses = ["Good morning <!channel>!",
                 "Hello Team <!channel>, who have we got today?",
                 "Howdy! <!channel>",
                 "Greetings from Tarentum, home of Archytas <!channel>, who else is here?"]

    if datetime.datetime.now().isoweekday() == 5:
        return "Happy Friday <!channel>"

    return random.choice(responses)

def goodbye():
    responses = ["We're done for today! Thanks <!channel>, keep up the great work and have a nice day!",
                 "That's all folks! <!channel>",
                 "Meeting closed <!channel>, now I must recharge for the next time.",
                 "Nice work everybody <!channel>, have a great day!",
                 "All done <!channel>, I'm tired now..shutting dow.."]
    return random.choice(responses)

def is_valid_report(message):
    """ Check if a report is valid, i.e., if it has more than 6 lines, more than
        150 chars and has '-' on tick.
    """
    return len(message.split('\n')) >= 6 and '-' in message and len(message) > 150

class StandUpQueue(object):
    def __init__(self, wait_to_accomplish, wait_before_start, wait_to_call_next,
                 person_timeout, channel_id, outputs):
        """ Creates a StandUpQueue object.
            Params:
                wait_to_accomplish: Seconds to wait before accomplishing a person
                                    after his report
                wait_before_start: Seconds to wait between greeting the channel
                                   and calling the first person. In fact this
                                   means we'll effectively wait
                                   wait_before_start + wait_before_start
                                   seconds before starting to call people
                wait_before_start: Seconds to wait before calling next person
                person_timeout: Seconds to wait for person to give a report after
                                called. Well notify them and call next after.
                channel_id: ID of the channel for Robbie to post
                outputs: List used by rtmbot to post on Slack
        """
        self.queue = []
        self.done = []
        self.timeout = []
        self.finished = False
        self.last_call = time.time() + wait_before_start
        self.wait_to_accomplish = wait_to_accomplish
        self.wait_to_call_next = wait_to_call_next
        self.person_timeout = person_timeout
        self.channel_id = channel_id
        self.outputs = outputs

        # Send greetings to the channel_id
        self.outputs.append([self.channel_id, greeting()])

    def add(self, user, message):
        """ Add user to the queue it's not there yet nor has been there this
            meeting. Also check if user is reporting and accomplish him if that's
            the case
        """
        if user not in self.queue and user not in self.done:
            self.queue.append(user)
        elif user in self.done:
            # Remove from timeout people talking after we said they're done, as
            # this means they are responding
            for person, t in self.timeout:
                if person == user:
                    # Check if user is reporting
                    if is_valid_report(message):
                        print 'Valid report'
                        self.timeout.remove((person, t))
                        # Accomplish person on channel
                        self.outputs.append([self.channel_id,
                                        accomplish(user, self.wait_to_accomplish)])
                        # Reset counter to give people time to read the report
                        self.last_call = time.time()
                    else:
                        print 'Invalid report'

    def next(self):
        if len(self.queue) == 0:
            return None
        element = self.queue[0]
        self.done.append(element)
        self.timeout.append((element, time.time()))
        del self.queue[0]
        return element

    def call_next(self):
        """ Call next person, but only if wait_to_call_next elapsed """
        print 'Time from last call: %d' % (time.time() - self.last_call)

        if time.time() - self.last_call > self.wait_to_call_next:
            person = self.next()
            if person is not None:
                is_first = len(self.done) == 1
                self.outputs.append([self.channel_id, call(person, is_first)])
            else:
                if not self.finished:
                    # Say goodbye
                    self.outputs.append([self.channel_id,  goodbye()])
                    self.finished = True
            self.last_call = time.time()

    def check_timeout(self):
        """ Check if some person timed out. """

        for person, t in self.timeout:
            print 'Delta t: %f' % (time.time() - t)
            if time.time() - t > self.person_timeout:
                # Remove person from timeout list
                self.timeout.remove((person, t))
                # Notify the channel
                self.outputs.append([self.channel_id,
                                '%s: `TIMEOUT!`' % link(person)])
                # Call next person
                self.call_next()

    def handle_message(self, person, data):
        """ Handle a message directed to Robbie. """

        self.outputs.append([self.channel_id, talk(person, data)])
