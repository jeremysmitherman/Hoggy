from setup import quotes
import re
#from sqlalchemy import *
import random

class ActionException(Exception):
    def __init__(self, message):
        super(ActionException, self).__init__(message)

class command(object):
    shortdesc = "No help available"
    longdesc = "No help available, try !eject"

    def execute(self, *args):
        raise NotImplementedError

class hoggy(command):
    longdesc = "with no arguments will display a random quote.  [add <quote>] will add the specified <quote> to the db. [#] Will display the quote with the specified ID"
    shortdesc = "Display or add Hoggyisms"

    # Hoggyism operations
    def add_quote(self, message):
        q = quotes.insert()
        return q.execute(body=message)

    def get_random(self):
        q =  quotes.select(limit=1).order_by('RANDOM()')
        rs = q.execute()
        row = rs.fetchone()
        return row

    def get_by_id(self, quoteId):
        q =  quotes.select().where('id=' + str(quoteId))
        rs = q.execute()
        row = rs.fetchone()
        return row

    def remove_quote(self, quoteId):
        q = quotes.delete().where("id=" + str(quoteId))
        q.execute()

    @classmethod
    def execute(cls, *args, **kwargs):
        hog = cls()
        argc = len(args)
        if argc == 0:
            row = hog.get_random()
            return '%s (#%d)' % (str(row['body']), row['id'])

        elif argc == 1:
            try:
                quoteId = int(args[0])
                row = hog.get_by_id(quoteId)
                return '%s (#%d)' % (str(row['body']), row['id'])
            except:
                return '!help for usage'

        elif args[0] == 'add':
            string = " ".join(args[1:])
            string = unicode(string)
            quoteId = hog.add_quote(string)
            return "Added %s" % str(string)

        elif args[0] == 'remove':
            try:
                quoteId = int(args[1])
            except:
                return '!help'

            hog.remove_quote(quoteId)
            return "Deleted #%d" % quoteId

class eject(command):
    shortdesc = "Get the hell out of Dodge!"
    longdesc = "Leave the room in style."

    @classmethod
    def execute(cls, user, client):
        client.kick('hoggit', user, 'Ejecting!')
        return "EJECT! EJECT! EJECT! " + user + " punched out."

class guns(command):
    shortdesc = "Strike down a target with great vengeance and furious anger"
    longdesc = "Seriously, great vengeance and furious anger"

    @classmethod
    def execute(cls, user, client=None):
        return 'BBBRRRRRRRAAAAPPPPPPPPPP!!!!'

class rifle(command):
    shortdesc = "Fire a AGM-65"
    longdesc = "No arguments fires one into the great blue yonder. [<target>]:  attempts to destroy <target>"

    @classmethod
    def execute(cls, target = None, user = None, client=None):
        if target is None:
            return '(M) BBBBEEEEEEPPPPPP!  EVERYONE FLIP THE FUCK OUT'
        try:
            message = '%s slews over to the burning hot flesh-sack that is %s with an AGM-65 seeker....\n' % (user, target)
            message += '(M) BBBBEEEEEEPPPPPP!  EVERYONE FLIP THE FUCK OUT\n'
            if random.randint(0,100) > 33:
                message += '%s obliterated %s with a well aimed Maverick.' % (user, target)
            else:
                message += '%s missed, the seeker locked onto a nearby moose in flight.' % user
        except Exception, ex:
            print ex
            message = '(M) BBBBEEEEEEPPPPPP!  EVERYONE FLIP THE FUCK OUT'

        return message

class pickle(command):
    @classmethod
    def execute(cls, target = None, user = None, client = None):
        if target is None:
            messages = [
                'dropped his bombs without looking, and demolished an elementary school.  The horror is etched into the minds of generations to come.',
                'dropped his bombs with no target and and destroyed the penguin exhibit at the local zoo.  The screams can still be heard to this day',
                'dropped his bombs without looking, inadvertanly starting a war with New Zealand.'
            ]

            message = messages[random.randint(0,2)]
            return user + ' ' + message

        message = '%s dropped a high angle CCIP Mk. 82 toward %s\n' % (user, target)
        if random.randint(0,100) > 33:
            message += '%s obliterated %s with a well aimed Drop.' % (user, target)
        else:
            message += '%s missed, read the 9-line noob!' % user

        return message


class print_help(command):
    @classmethod
    def execute(cls, *args, **kwargs):
        argc = len(args)
        to_ret = ""
        if argc == 0:
            to_ret = "Type help <command> for more detailed information.\n"
            for key,cls in Commander.actions.iteritems():
                to_ret += "%s: %s\n" % (key, cls.shortdesc)

            return to_ret

        if argc == 1:
            #found = False
            searchcls = args[0]
            if not searchcls.startswith('!'):
                searchcls = "!" + searchcls
            try:
                comclass = Commander.actions[searchcls]
            except:
                raise ActionException('Invalid command: ' + cls)

            return searchcls + ": " + comclass.longdesc

class Commander(object):
    actions = {
        '!hoggy':hoggy,
        '!guns' : guns,
        '!rifle': rifle,
        '!pickle': pickle,
	    '!eject':eject,
        '!help': print_help
    }

    def __init__(self, client):
        self.client = client

    def recv(self, message, user):
        if message.startswith('!'):
            # Awww snap, it's a hoggy action
            try:
                # split up the command into action and args
                command_array = message.split(' ')
                command = command_array[0]
                
                # Check that there are args, if not args is empty list
                if len(command_array) > 1:
                    try:
                        args = command_array[1:]
                    except:
                        args = []
                else:
                    args = []

                # Attempt to find a corresonding registered action
                try:
                    action = self.actions[command]
                except:
                    raise ActionException('Invalid command: ' + command)

                return action.execute(*args, user=user, client=self.client)
            except ActionException, ex:
                return str(ex)
            except Exception, ex:
                return "Hoozin'ed it up: unexpected exception: " + str(ex)
        else:
            if  message.startswith('r/') or ' r/' in message:
                obj = re.search('r/[^\s\n]*',message)
                sub = obj.group()
                if sub.startswith('/'):
                    sub = sub[1:]
                return "http://reddit.com/%s" % sub

            if  message.startswith('u/') or ' u/' in message:
                obj = re.search('u/[^\s\n]*',message)
                sub = obj.group()
                if sub.startswith('/'):
                    sub = sub[1:]
                return "http://reddit.com/%s" % sub


