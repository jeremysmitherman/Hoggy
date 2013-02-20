from setup import quotes
from random import choice
import re
#from sqlalchemy import *
import random
import requests

class ActionException(Exception):
    def __init__(self, message):
        super(ActionException, self).__init__(message)

class command(object):
    shortdesc = "No help available"
    longdesc = "No help available, try !eject"

    def execute(self, *args):
        raise NotImplementedError

class no(command):
    longdesc = "For use in dire situations only."
    shortdesc = "For dire situations."
    
    @classmethod
    def execute(cls, *args, **kwargs):
        return "http://nooooooooooooooo.com/"

class blame(command):
    longdesc = "No seriously, fuck that guy."
    shortdesc = "Fuck that guy."

    @classmethod
    def execute(cls, *args, **kwargs):
        if not len(args):
            return "Usage: !blame <user>"
        if args[0].lower() == 'hoozin':
            return "^"
        elif args[0].lower() == 'hoggy':
            return "What'd I do?"
        return "Dammit, %s.  Now you've gone and Hoozin'ed it up." % args[0]

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
    
    def search(self, message):
        print "Search string: "+ message
        q = quotes.select().order_by('id').where('body LIKE "%'+message+'%"')
        print q
        rs = q.execute()
        rows = rs.fetchall()
        return rows

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
            if hog.remove_quote(quoteId):
                return "Deleted #%d" % quoteId
            else:
                return "No quote with id: %s" %quoteId
        elif args[0] == 'search':
            try:
                search_string = str(args[1])
                if (len(search_string) < 3):
                    return "Minimum search requires 3 letters"
            except:
                return "L2P"
            
            results = hog.search(search_string)
            return_string = ""
            for result in results:
                return_string += "#%d: \"%s\"\n" % (result[0], result[1])
       
            return return_string.encode('ascii','replace')        
        else:
            return "Invalid usage. Check help."


class grab(command):
    shortdesc = "Grab the last n lines of a specifc user and create a hoggyism"
    longdesc = "Usage: !grab <user> <number of lines>  number of lines defaults to 1"

    @classmethod
    def execute(cls, *args, **kwargs):
        if len(args) == 1:
            num_lines = 1
        else:
            try:
                num_lines = int(args[1])
	    except:
                num_lines = 0

        if num_lines < 1:
            return kwargs['user'] + "... Don't be a dipshit."

	if args[0].lower() == 'hoggy':
            return "Got no time to be playing with myself..."

        quote = kwargs['client'].grabber.grab(args[0], num_lines)
	return hoggy.execute('add', quote)
	

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

class wire(command):
    @classmethod
    def execute(cls, target = None, user = None, client = None):
        if target is None:
            messages = [
                "launches a Vikhir at empty space. Can't be worse than aiming at something."
            ]
            return "%s %s" % (user, choice(messages))
        elif target.lower() == user.lower():
            messages = [
                "manages to fire a Vikhir at themself. Lasers aren't for pointing into cockpits. Naughty!"
            ]
            return "%s %s" % (user, choice(messages)) 
        else:
            messages = [
                "but they crashed for no good reason",
                "it plowed into the ground",
                "it overshot the target",
                "it undershot the target",
                "but their laser burned out",
                "however their tail fell off",
                "but their autopilot flipped out",
                "but their trim reset",
                "and it hit the target! .... nah",
                "but it fell in love with a passing Hind and they embraced awkwardly"
            ]
            return "%s launched a Vikhir at %s, %s." % (user, target, choice(messages))

class print_help(command):
    @classmethod
    def execute(cls, *args, **kwargs):
        argc = len(args)
        to_ret = ""
        if argc == 0:
            to_ret = "Type help <command> for more detailed information.\n"
            for key,cls in Commander.actions.iteritems():
                to_ret += "%s: %s\n" % (key, cls.shortdesc)

            kwargs['client'].msg(kwargs['user'],to_ret)

        if argc == 1:
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
        '!help': print_help,
        '!no':no,
        '!grab': grab,
        '!blame' : blame,
        '!wire' : wire
    }

    def __init__(self, client):
        self.client = client


    def getYoutubeTitle(self, user, id):
        r = requests.get("".join(["http://gdata.youtube.com/feeds/api/videos/", id, "?v=2&alt=json"]))
        if r.status_code != 200:
            if r.status_code == 400:
                return user + ", why you gotta make life hard? Make it a good link."
            return "Youtube Hoozin'ed it up. (HTTP %d)" % r.status_code
        try:
            sec = int(r.json()['entry']['media$group']['media$content'][0]['duration'])
            min = sec / 60
            hr = min / 60
            sec = sec % 60
            min = min % 60
            title = r.json()['entry']['media$group']['media$title']['$t'].encode('utf-8')
            if hr != 0:
                return "%s [%02d:%02d:%02d]" % (title, hr, min, sec)
            else:
                return "%s [%02d:%02d]" % (title, min, sec)
        except IndexError:
            return user + ", that video isn't available or doesn't exist."

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
            
            #our youtube lookups, short and long have different formats
            YTshort = "youtu.be/" in message
            YTlong = "youtube.com/watch?" in message
            if YTshort or YTlong:
                parts = message.split()
                for part in parts:
                    if part.startswith('http:'):
                        if YTlong:
                            try:
                                id = part.split('v=')[1]
                            except IndexError:
                                return user + " Hoozin'ed that youtube link!"
                            id = id.split('&')[0]
                        elif YTshort:
                            id = part.rsplit('/', 1)[1]
                        return self.getYoutubeTitle(user, id)
                        