Hoggy
=====

Hoggy is an IRC Bot with some built in reddit oriented functionality.  He will report new threads when they are created, link to subreddits and users when they are detected in the chat, store out of context quotes and recall them on command, and has a bunch of A-10 related functionality to allow you to kill others in the room (with random success chance) per the original subreddit this guy was in use, /r/hoggit

Requirements
====

Hoggy needs the following Python modules:

* Twisted
* SQLAlchemy
* BeautifulSoup
* Requests

You can get all of the above really easily from PIP, so it's suggested that you run Hoggy in its own virtualenv (if you know how).

Installation
====

1. Make a copy of config.ini.default as config.ini, and open it in your favourite text editor.
2. Fill out config.ini, which should be fairly self explanatory. If you're using MySQL, make sure you create a database and user for Hoggy.
3. Execute setup.py to create the required database tables
4. Wonder how you didn't hoozin' it up

Usage
====

It is recommended to run hoggy in a screen, or with nohup.

With screen simply use "python hoggy.py <your channel> <logfile>"

With nohup use "nohup python hoggy,py <your channel> <logfile> &"

If there is no # at the start of your channel, it will be appended.  If you add it remember that it needs to be in quotes or your shell will interpret it wrong.

Known Bugs
====

There are some regex related issues with the subreddit and user linking,  subreddit's right now must be linked without the leading slash r/hoggit instead of /r/hoggit for example.

MySQL support is new and untested, but there's no reason that it shouldn't work.
