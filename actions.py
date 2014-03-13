from setup import quotes, times, engine, feeds, learn
from random import choice
from UserString import MutableString
import subprocess
import re, sys, threading, socket
import random
import requests
import time
import urllib
import BeautifulSoup
import praw
import time
from sidebar import template
from time import gmtime
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read(sys.argv[1])

class ActionException(Exception):
    def __init__(self, message):
        super(ActionException, self).__init__(message)

class command(object):
    shortdesc = "No help available"
    longdesc = "No help available, try !eject"

    def execute(self, *args):
        raise NotImplementedError

class ping(command):
    @classmethod
    def execute(cls, target=None, user = None, client = None):
        return choice(["Hoozin'd it up.  Naw Just kidding. Pong.", "pong", "pang", "poong", "ping?", "pop", "pa-pong!", "kill yourse- sorry, pong", "ta-ping!", "Wasn't that Mulan's fake name?"])

class when(command):
    shortdesc = "Gets the current time for the given user"
    longdesc = "Try !when <user>, requires that user to have done a !settime first"
    @classmethod
    def execute(cls, target = None, user = None, client = None):
        low = target.lower()
        if low == "hoggy":
            return "I am beyond both time and space, mortal"

        time =  times.select().where(times.c.name==low).execute().fetchone()
        if not time:
            return "They don't appear to have set a time yet, sorry"
        time = get_adjusted_time(time.time)
        return "The local time in {0}-land is: {1}".format(target, time)

def get_adjusted_time(adjustment):
    adj = gmtime(time.time()+adjustment*60*60)
    return time.strftime("%a %H:%M", adj)

class settime(command):
    shortdesc = "Set your timezone"
    wanted = "!settime [UTC|GMT][+|-]hours"
    longdesc = format
    @classmethod
    def execute(cls, time = None, user = None, client = None):
        if not time or not user:
            return
        reg = re.compile("^(ZULU|GMT|UTC)(\+|-)[0-9]{1,2}[:|\.]{0,1}[0-9]{0,2}$")
        if not reg.match(time):
            return "Hey, try the format: {0}".format(settime.wanted)
        dir = 1
        if '-' in time:
            dir = -1
        time = time[4:]
        if ':' in time:
            parts = time.split(':')
            if len(parts[1]) != 2:
                return "Two digits for minutes, thank you very muchly"
            hours = int(parts[0]) + (float(parts[1]) / 60.0)
        elif '.' in time:
            hours = float(time)
        else:
            hours = int(time)
        user = user.lower()
        hours *= dir
        if times.select().where(times.c.name==user).execute().fetchone():
            times.update().where(times.c.name==user).values(time=hours).execute()
        else:
            ins = times.insert()
            ins.execute(name=user, time=hours)
        return "Your clock is now set at {0}".format(get_adjusted_time(hours))

class urbandictionary(command):
    @classmethod
    def execute(cls, *args, **kwargs):
        r = requests.get("http://api.urbandictionary.com/v0/define?term={0}".format(" ".join(args)))
        json = r.json()
        defs = json['list']
        if not len(defs):
            return "No definintions found.  Try !eject."
        return "{0}: {1}".format(" ".join(args), defs[0]['definition'].encode('utf-8'))

class new(command):
    shortdesc = "Update the subreddit header with something extremely thought-provoking or insightful."
    longdesc = "Now with added sidebar garbling!"

    @classmethod
    def execute(cls, *args, **kwargs):
        if args[0] == '!hoggy':
            if int(args[1]):
                header = hoggy.execute(args[1])
            else:
                return "Usage: !new hoggy 15"
        else:
            header =  " ".join(args).replace("=","\=")

        manager = praw.Reddit("HoggyBot for /r/hoggit by /u/zellyman")
        manager.login(config.get('reddit', 'username'), config.get('reddit', 'password'))
        subreddit = manager.get_subreddit(config.get('reddit', 'subreddit'))
        settings = subreddit.get_settings()
        new_desc = "### %s \n=\n\n" % header
        new_desc += template

        subreddit.set_settings("Hoggit Fighter Wing", description=new_desc)

        return "Header updated."

class lightning(command):
    shortdesc = "THUNDER STRIKE"
    longdesc = "http://www.youtube.com/watch?v=j_ekugPKqFw"
    @classmethod
    def execute(cls, target = None, user = None, client = None):
        return "LIGHTNING BOLT! %s takes %d damage" % (target, random.randint(0,9999))

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
        messages = [
            "I concur, %s is absolutely responsible.",
            "Dammit, %s, now you've gone and Hoozin'ed it up."
        ]
        return choice(messages) % args[0]

class hoggy(command):
    longdesc = "with no arguments will display a random quote. [#] will display the quote with the specified ID. [add <quote>] will add the specified <quote> to the db. [search <string>] will look for that string in the db. [count] should show the number of hoggyisms stored."
    shortdesc = "Display or add Hoggyisms"

    # Hoggyism operations
    def add_quote(self, message):
        q = quotes.insert()
        q.execute(body=message)
        return engine.scalar("select max(id) from quotes")

    def get_random(self):
        q =  quotes.select(limit=1).order_by('RANDOM()')
        rs = q.execute()
        row = rs.fetchone()
        return row

    def search(self, message):
        q = quotes.select().order_by('id').where('body LIKE "%{0}%"'.format(message))
        rs = q.execute()
        rows = rs.fetchall()
        return rows

    def get_by_id(self, quoteId):
        q =  quotes.select().where('id=' + str(quoteId))
        rs = q.execute()
        row = rs.fetchone()
        return row

    def remove_quote(self, quoteId):
        q = quotes.delete().where("id={0}".format(str(quoteId)))
        q.execute()
    def count(self): return quotes.count()

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
                if quoteId == 1000:
                    return "I'm really sorry, %s.  I really wanted to make a wonderful 1000 GET for you, but %s ruined it for everyone." % (kwargs['user'], choice(['Iron', "Hoozin","Jers"]))
                row = hog.get_by_id(quoteId)
                return '%s (#%d)' % (str(row['body']), row['id'])
            except:
                return '!help for usage'

        elif args[0] == 'add':
            string = " ".join(args[1:])
            string = unicode(string)
            quoteId = hog.add_quote(string)

            return "Added {0} (#{1})".format(str(string), quoteId)

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
            return "http://hoggit.us/search?query=%s" % " ".join(args[1:])
        elif args[0] == 'count':
            number = hog.count()
            return "There are currently {0} hoggyisms stored!".format(number)
        else:
            return "You hoozed it up, do !help hoggy"


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
            return "{0}... Don't be a dipshit.".format(kwargs['user'])

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
        return "EJECT! EJECT! EJECT! {0} punched out.".format(user)

class guns(command):
    shortdesc = "Strike down a target with great vengeance and furious anger"
    longdesc = "Seriously, great vengeance and furious anger"

    @classmethod
    def execute(cls, target = None, user = None, client=None):
        if target is None:
            return 'BBBRRRRRRRAAAAPPPPPPPPPP!!!!'
        try:
            message =  "%s sets up a gun run...\n" % (user)

            if random.randint(0,100) > 33:
                message += "BBBRRRRRRRAAAAPPPPPPPPPP!!!! \n"
                message += "%s pulverized %s with great vengeance and furious anger" % (user, target)
            elif random.randint(0,100) > 60:
                message += "%s screwed up their attack run, but managed to pull out." % (user)
            else:
                message += "%s ignored the VMU's 'PULL UP' and smashed into %s" % (user, target)
                client.kick('hoggit', user, 'Is no more.')
        except Exception, ex:
            print ex
            message = "%s screwed up their attack run, but managed to pull out." % (user)

        return message

class thanks(command):
    shortdesc = "For polite people only"
    longdesc = "Like this ever gets any use"

    @classmethod
    def execute(cls, target = None, user = None, client=None):
        if target is not None:
            return "What about me?"
        else:
            return "No problem, %s" % (user)

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
    shortdesc = "Drop the bombs of peace onto the target of desperation"
    longdesc = "Like this will ever hit anything"

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
        elif target.lower() == user.lower():
           client.kick('hoggit', user, 'Self-immolation is not the way forward')
           return "%s rolls 180 degrees and drops his bombs... before realising what a silly mistake he made" % user
        bombs = [
            'Mk. 82',
            'Mk. 84',
            'CBU-87',
            'CBU-97',
            'GBU-10',
            'GBU-12',
            'GBU-38',
            'GBU-31'
        ]
        types = [ 'CCIP', 'CCRP' ]
        message = '%s released a %s %s toward %s\n' % (user, choice(types), choice(bombs), target)
        if random.randint(0,100) > 33:
            message += '%s obliterated %s with a well aimed Drop.' % (user, target)
        else:
            message += '%s missed, read the 9-line noob!' % user

        return message

class wire(command):
    shortdesc = "Accurately simulates a Vikhir missile"
    longdesc = "Good luck hitting anything"

    @classmethod
    def execute(cls, target = None, user = None, client = None):
        if target is None:
            messages = [
                "launches a Vikhir at empty space. Can't be worse than aiming at something."
            ]
            return "%s %s" % (user, choice(messages))
        elif target.lower() == user.lower():
            messages = [
                "manages to fire a Vikhir at themself. Lasers aren't for pointing into cockpits. Doesn't mattter much though, it still missed."
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

class ron(command):
    shortdesc = "Why the fuck would you use this command? It's a complete waste of time."
    longdesc = "Kill yourself"

    @classmethod
    def execute(cls, target = None, user = None, client = None):
        if target is not None:
            return "%s, you little fuck." % (target)
        else:
            messages = [
                "I would smack you in the mouth if I wouldn't feel bad for hitting a retard afterwards.",
                "If you project Excel, there better be fucking numbers in it somewhere.",
                "I would trade 3 of you for a talking version of Wikipedia or Wolfram Alpha. Seriously, don't get comfortable fucksticks.",
                "It's not rape if you yell out \"SURPRISE!\"",
                "Windows Vista was like a whore house when the ships come in",
                "\"Hush you I'm recalling the time Ron sent me cocaine via USPS\"",
                "\"\"Listen,\" he said, leaning closer, \"I\'m a fucking piranha in this pool. All these other socially awkward people, I eat them up. That\'s right, fucker,\" he added. \"That\'s just how I roll.\" He grabbed a woman seated to his right. A tattoo of a tree covered her back. George pointed. I looked. A small R.G. was nestled on one of the branches.  --RonUSMC\"",
                "Ron doesn\'t miss you, fuck you.",
                "Ron\'s a fucking piranha in this pool",
                "What\'s up, faggots? --Ron"
            ]
            return "%s" % (choice(messages))



class hug(command):
    shortdesc = "Hoggit is not responsible for any rape allegations that may arise from using this command"
    longdesc = "It makes me cringe when I think about it"

    @classmethod
    def execute(cls, target = None, user = None, client = None):
        if target is None:
            return "What, hug myself?"
        elif target.lower() == user.lower():
            return "Hugging yourself? Keep it clean!"
        else:
            return "%s gives %s a lingering hug. %s likes it. Likes it a lot...\nThey continue their embrace, %s gently stroking %s's face, and %s leans in for a kiss." % (user, target, target, target, user, user)

class print_help(command):
    shortdesc = "Cause a infinite loop by reading the help out again"
    longdesc = "This isn't good for the environment you know"

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
                searchcls = "!{0}".format(searchcls)
            try:
                comclass = Commander.actions[searchcls]
            except:
                raise ActionException('Invalid command: ' + cls)

            return "{0}: {1}".format(searchcls, comclass.longdesc)

class roll(command):
    shortdesc ="Roll them bones"
    longdesc = "Randomly generates some numbers given input in the format of <number of dice>d<number of sides> ie: 1d20 will roll a single 20 sided die. Maximum 10 dice and 100 sides"

    @classmethod
    def execute(cls, *args, **kwargs):
        if len(args) != 1:
            return Commander.insult(kwargs['user'])
        try:
            darray = args[0].split("d")
            numdice = int(float(darray[0]))
            numsides = int(float(darray[1]))
            if numdice <= 0 or numdice > 10 or numsides <= 0 or numsides > 100 or (float(darray[0]) != int(darray[0])) or (float(darray[1]) != int(darray[1])) :
                return Commander.insult(kwargs['user'])

            dice = []
            total = 0
            for i in range(numdice):
                die = random.randint(1, numsides)
                dice.append(die)
                total += die
            if numdice > 1:
                return 'Go! Dice Roll! ' + ', '.join([str(x) for x in dice]) + ' (' + str(total) + ')'
            else:
                return ' '.join([str(x) for x in dice])
        except:
            return Commander.insult(kwargs['user'])



class choose(command):
    shortdesc = "Chooses something"
    longdesc = "Picks a random string given input in the format <string> or <string> or <string>.... etc."

    @classmethod
    def execute(cls, *args, **kwargs):
        if len(args) == 0:
            return Commander.insult(kwargs['user'])

        temp = ' '.join([str(x) for x in args])
        return "Hmm, let's go with {0}".format(choice(temp.split("or")).strip())

class fortune(command):
    shortdesc = "CRYPTIC METAPHOR"
    longdesc = "You can try !fortune long for a longer fortune too!"

    @classmethod
    def execute(cls, *args, **kwargs):
        if len(args) == 1 and args[0] == "long" :
            temp = MutableString()
            for line in subprocess.check_output(["fortune", "-l"]).split("\n"):
                temp += str(line)
                temp += ' '
            kwargs['client'].msg(kwargs['user'], temp)
        else :
            temp = MutableString()
            for line in subprocess.check_output("fortune").split("\n"):
                temp += str(line)
                temp += ' '
            return temp;

class what(command):
    shortdesc = "Gets what something is"
    longdesc = "Accepts !what <something> and !what is <something>"

    def get_learn(self, key):
        l = learn.select().where(learn.c.key==key)
        le = l.execute();
        rs = le.fetchall();

        if len(rs) == 0 :
            return choice(["I don't know nothin", "Nope sorry, can't recall", "Err...nothing", "Still negative function on that one"]);
        output = key + " is: "
        count = 1
        for row in rs:
            output += str(row[2]) + " (" + str(count) + "), "
            count += 1
            if count == 10 :
              output += "and more ..."
              return output

        return output[:-2]

    @classmethod
    def execute(cls, *args, **kwargs):
        if len(args) != 1 and len(args) != 2:
            return Commander.insult(kwargs['user'])
        elif len(args) == 2 and args[0] == "is":
            return cls().get_learn(args[1])
        else:
            return cls().get_learn(args[0])

class learncom(command):
    shortdesc = "I want to learn something!"
    longdesc = "Input is accepted as <something> is <something>: ie Hoozin is somebody with no self esteem"


    def add_learn(self, lkey, lrelation, ladd):
        l = learn.insert()
        l.execute(key = lkey, relation = lrelation, added = ladd)

    @classmethod
    def execute(cls, *args, **kwargs):
        if len(args) == 0:
            return Commander.insult(kwargs['user'])

        temp = ' '.join([str(x) for x in args])
        temp = temp.split('is')
        if len(temp) != 2:
            return Commander.insult(kwargs['user'])

        cls().add_learn(temp[0].strip(), temp[1].strip(), kwargs['user'].strip())
        return choice(["Sure thing, pal", "Okay, why not?", "Yeah I don't mind", "I'll write that one down", "Roger, {0}".format(kwargs['user']), "For you, {0}? Anything.".format(kwargs['user'])])

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
        '!wire' : wire,
        '!hug' : hug,
        '!ron' : ron,
        '!thanks' : thanks,
        '!ron': ron,
        '!bolt': lightning,
        '!new': new,
        '!when': when,
        '!settime':settime,
        '!ud': urbandictionary,
        '!ping':ping,
        '!dice':roll,
        '!choose':choose,
        '!quote':fortune,
        '!learn':learncom,
        '!what':what
    }

    @classmethod
    def insult(self, user):
        return choice([ "What? no",
                        "Look don't be stupid now {0}".format(user),
                        "Hey don't look now but there is one man too many in this room and I think it's {0}".format(user),
                        "That won't work. Have you tried !eject ?",
                        "I don't support the stupidity movement so I can't help you with that",
                        "....what",
                        "Stop {0}. What are you doing {0}. Stop.".format(user),
                        "Wow not even Hoozin could screw up that badly. I'm impressed {0}".format(user),
                        "Have you tried being smarter? ...You have? I'm so sorry for you",
                        "This bot does not accept input of that much ... creativity",
                        "Why don't you go home to your wife? Better yet, I'll go home to your wife, and outside of the improvement, she won't notice any difference",
                        "I want to thank you for all the enjoyment you've taken out of being a bot",
                        "Look even a five year old would understand how to use that command. Fetch a five year old.",
                        "{0} may act like an idiot and type like an idiot but don't let that fool you. He really is an idiot".format(user),
                        "[INCORRECT BOT COMMANDS ITENSIFIES]",
                        "Hold on I changed how that command works. It's now !eject",
                        "You know I could rent you out as a decoy for duck hunters, {0}?".format(user),
                        "Stop that you'll anger the jers",
                        "I never forget a command, but in your case i'll make an exception",
                        "Calling you an idiot for that would be an insult to stupid people everywhere",
                        "I don't know what your problem is {0}, but I bet it is hard to pronounce".format(user),
                        "Don't you need a license to be that stupid?",
                        "Dear Diary: Today, {0} was a faggot".format(user),
                        "No way! No way! No way! No way!",
                        "Have you tried reading the help?",
                        "Incorrect! Try again",
                        "No no no you that's not how you do it",
                        "If the last command was any indication of this channel this channel is going to blow",
                        "This is like when I plateaued on the delts, man",
                        "We're gonna need both horsepowers on this thing to figure that one out",
                        "Let's pretend that never happened, okay?",
                        "I hope {0}-senpai notices me ... and learns to stop fucking up the bot commands".format(user)])

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
                return "Hoozin'ed it up: unexpected exception: {0}".format(str(ex))
        else:
            if  ' r/' in message or '/r/' in message:
                obj = re.search(r'[/]?r/[^\s\n]*',message)
                sub = obj.group()
                if sub.startswith('/'):
                    sub = sub[1:]
                return "http://reddit.com/%s" % sub

            if  ' u/' in message or '/u/' in message:
                obj = re.search(r'[/]?u/[^\s\n]*',message)
                sub = obj.group()
                if sub.startswith('/'):
                    sub = sub[1:]
                return "http://reddit.com/%s" % sub

            if "http" in message:
                parts = message.split()
                for part in parts:
                    if part.startswith('http:') or part.startswith('https:'):
                        soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(part))
                        try:
                            return "Title: {0}".format(soup.title.string.encode('ascii', 'ignore'))
			except:
                            pass

