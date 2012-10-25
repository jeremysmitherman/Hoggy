Hoggy
=====

Hoggy is an IRC Bot with some built in reddit oriented functionality.  He will report new threads when they are created, link to subreddits and users when they are detected in the chat, store out of context quotes and recall them on command, and has a bunch of A-10 related functionality to allow you to kill others in the room (with random success chance) per the original subreddit this guy was in use, /r/hoggit

Installation
====

Hoggy requires Twisted, SQLAlchemy, and Requests.  All easily obtainable from pip, therefore it's recommended to run Hoggy in his own virtualenv.
Once the prereqs are installed, run python setup.py.  This creates the sqlite database needed for the quotes.

Usage
====

It is recommended to run hoggy in a screen, or with nohup.

With screen simply use "python hoggy.py <your channel> <logfile>"

With nohup use "nohup python hoggy,py <your channel> <logfile> &"

If there is no # at the start of your channel, it will be appended.  If you add it remember that it needs to be in quotes or your shell will interpret it wrong.

Known Bugs
====

There are some regex related issues with the subreddit and user linking,  subreddit's right now must be linked without the leading slash r/hoggit instead of /r/hoggit for example.