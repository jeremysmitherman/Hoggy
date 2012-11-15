from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
#from twisted.python import log
#import re
from sqlalchemy import create_engine, MetaData
import redditupdate

import time#, sys, random
import os
import ConfigParser
import logging

import actions

HERE =  os.path.dirname(os.path.abspath(__file__))
engine = create_engine('sqlite:///%s.sqlite' % HERE)
metadata = MetaData(engine)

try:
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    fh = logging.FileHandler(config.get('hoggy', 'logfile'))
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
    fh.setFormatter(formatter)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    log.addHandler(sh)
    log.addHandler(fh)
except ConfigParser.NoSectionError:
    print "Config file is un-readable or not present.  Make sure you've created a config.ini (see config.ini.default for an example)"
    exit()

class MessageLogger:
    def __init__(self, logFile):
        self.logFile = logFile

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class HoggyBot(irc.IRCClient):
    """A logging IRC bot."""
    nickname = config.get('irc', 'nick')

    def __init__(self, *args, **kwargs):
        self.commander = actions.Commander(self)

    # callbacks for events
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

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % channel)
        self.reddit_update = redditupdate.RedditUpdateThread(self, channel)
        self.reddit_update.parse_threads(self.reddit_update.request_threads(),False)
        self.reddit_update.start()

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            message = self.commander.recv(msg,user)
            self.msg(user, message)
            return

        message = self.commander.recv(msg, user)
        if message:
            self.msg(channel, message)

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



class HoggyBotFactory(protocol.ClientFactory):
    """A factory for HoggyBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p = HoggyBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # create factory protocol and application
    f = HoggyBotFactory(config.get('irc', 'channel'), config.get('irc', 'log'))

    # connect factory to this host and port
    reactor.connectTCP(config.get('irc', 'host'),config.getint('irc', 'port') , f)

    # run bot
    reactor.run()
