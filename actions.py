from hoggy import HoggyBot
from setup import quotes
from sqlalchemy import *

class ActionException(Exception):
    def __init__(self, message):
        super(ActionException, self).__init__(message)

class command(object):
    def execute(self, *args):
        raise NotImplementedError

class Commander(object):
    actions = {
        '!hoggy':hoggy
    }

    def recv(self, message):
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

                return action.execute(args)


class hoggy(command):
    # Hoggyism operations
    def add_quote(self, message):
        q = quotes.insert()
        return q.execute(body=message)

    def get_random(self):
        q =  quotes.select(limit=1).order_by('RANDOM()')
        rs = q.execute()
        row = rs.fetchone()
        return str(row['id']) +': ' + str(row['body'])

    def remove_quote(self, id):
        q = quotes.delete().where("id=" + str(id))
        rs = q.execute()

    def execute(self, *args):
        argc = len(args)
        if argc == 0:
            return self.get_random()

        elif if argc == 1:
            return '!help for usage'

        elif args[0] == 'add':
            string = " ".join(args[1:])
            string = unicode(string)
            id = self.add_quote(string)
            return "Added " + string + " (#" + str(id) + ")"


