# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
import re
from sqlalchemy import *
from  sqlalchemy.sql.expression import func

# system imports
import time, sys, random
import os

HERE =  os.path.dirname(os.path.abspath(__file__))

engine = create_engine('sqlite:///%s.sqlite' % HERE)

metadata = MetaData(engine)

from setup import quotes

class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    nickname = "hoggy"

    def add_quote(self, message):
        q = quotes.insert()
        q.execute(body=message)

    def get_random(self):
        q =  quotes.select(limit=1).order_by('RANDOM()')
        rs = q.execute()
        row = rs.fetchone()
        return str(row['id']) +': ' + str(row['body'])

    def remove_quote(self, id):
        q = quotes.delete().where("id=" + str(id))
        rs = q.execute()

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))
        self.logger.close()


    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        message = False

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if 'r/' in msg:
            obj = re.search('r/[^\s\n]*',msg)
            sub = obj.group()
            if sub.startswith('/'):
                sub = sub[1:]
            message = "http://reddit.com/%s" % sub

        if msg.startswith('!'):
            command = msg.split(' ')
            action = command[0]

            if action == '!test':
                message = "I'm awake! Stop poking me!"
            elif action == '!blame':
                try:
                    target = command[1]
                except:
                    message = '!blame requires a target'
                    self.msg(channel, message)
                    return
                message = "Well done, %s, you've done gone and Hoozin'ed it now." % target
            elif action == '!quit' or action == '!crash':
                message = 'Never'

            elif action == '!help':
                message = '!test\n!blame [target]\n!hoggy: Display a random Hoggyism\n!hoggy add [quote]: preserve a quote for all eternity\n!hoggy delete [id]\n!rifle [target](optional)\n!pickle [target]\n!guns'

            elif action == '!pickle':
                try:
                    target = command[1]
                except:
                    message = '!pickle requires a target'
                    self.msg(channel, message)
                    return
                message = '%s dropped a high angle CCIP Mk. 82 toward %s' % (user, target)
                self.msg(channel, message)
                if random.randint(0,100) > 33:
                    message = '%s obliterated %s with a well aimed drop.' % (user, target)
                else:
                    message = '%s missed, read the 9-line, noob!' % user

            elif action == '!guns':
                message = 'BBBBBBRRRRRRRAAAAAAAAAPPPPPPP!!!!!'

            elif action == '!rifle':
                message = ''
                try:
                    target = command[1]
                    message = '%s slews over to the burning hot flesh-sack that is %s with an AGM-65 seeker....\n' % (user, target)
                    message += '(M) BBBBEEEEEEPPPPPP!  EVERYONE FLIP THE FUCK OUT\n'
                    if random.randint(0,100) > 33:
                        message += '%s obliterated %s with a well aimed Maverick.' % (user, target)
                    else:
                        message += '%s missed, read the 9-line, noob!' % user
                except:
                    message = '(M) BBBBEEEEEEPPPPPP!  EVERYONE FLIP THE FUCK OUT'

            if action == '!hoggy':
                try:
                    original = command
                    command = command[1]
                except:
                    message = self.get_random()
                    self.msg(channel, message)
                    return

                if command == 'add':
                    print 'adding: ' + " ".join(original[2:])
                    self.add_quote(" ".join(original[2:]))
                    message = "Added: " + " ".join(original[2:])

                if command == 'delete':
                    try:
                        print original[2]
                        self.remove_quote(original[2])
                        message = "Removed Hoggyism " + original[2]
                    except Exception, ex:
                        print ex
                        message = 'delete requires quote id'
                        self.msg(channel, message)

        if message != False:
            self.msg(channel, message)
            self.logger.log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'



class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p = LogBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    f = LogBotFactory(sys.argv[1], sys.argv[2])

    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    print 'running reactor'
    reactor.run()