import requests
import threading
import json
import pickle
import logging
import time
import ConfigParser,sys

config = ConfigParser.RawConfigParser()
config.read(sys.argv[1])

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('redditthread.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
fh.setFormatter(formatter)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

log.addHandler(sh)
log.addHandler(fh)

class RedditUpdateThread(threading.Thread):
    new_url = 'http://www.reddit.com/r/'+ config.get('reddit','subreddit')+ '/new.json'
    stop_event = threading.Event()
    
    def __init__(self, client, channel):
        log.info('INIT RedditUpdateThread...')
        threading.Thread.__init__(self)
        self.daemon = True
        self.isRunning = True
        self.client = client
        self.channel = channel
        self.seenFile=config.get('hoggy','seenfile')
        self.session = requests.session()
        log.debug('RedditUpdateThread set to channel %s', self.channel)

        log.info('Loading seen threads...')
        try:
            with open(self.seenFile) as seen_threads_file:
                self.seen_threads = pickle.load(seen_threads_file)
        except IOError:
            log.debug(self.seenFile + ' either doesn\'t exist or is non-editable.  Creating new seen_threads.dat')
            self.seen_threads = []
            open(self.seenFile, 'w').close()
        
        except EOFError:
            log.debug('seen_threads exists but is empty.  Continuing...')
            self.seen_threads = []

        log.info('Loaded %d seen threads.', len(self.seen_threads))
        self.login()
  
    def run(self):
        log.info('Starting main loop')
        self.parse_threads(self.request_threads(), False)
        while self.isRunning:
            log.debug('Enter main loop...')
            self.parse_threads(self.request_threads())
            if self.stop_event.wait(30) == True:
                self.isRunning = False
            
        log.info('Left main loop.')
        
    def request_threads(self):
        log.debug('Requesting new threads...')
        headers = {"User-Agent":"New Thread updater.  /u/'+config.get('reddit','username')+' for /r/hoggit"}
        try:
            req = self.session.get(self.new_url, headers=headers)
        except:
            pass

        if req.status_code != 200:
            log.info('Failed getting new threads.')
        else:
            try:
                data = json.loads(req.text)
                if not data['data']['children']:
                    # Bot was probably logged out for some reason
                    self.login()
            except ValueError:
                log.warn('ValueError when attempting to loadJson: [' + req.text +']')
            threads = data['data']['children']
            #self.parse_threads(threads)
            return threads
        
    def parse_threads(self, threadlist,verbose=True):
        try:    
            for t in threadlist:
                if t['data']['id'] not in self.seen_threads:
                    #This won't spew out things on its first run when creating the threads
                    if verbose:
                        self.client.msg(self.channel, "NEW THREAD BY " + str(t['data']['author'])  + ": " + str(t['data']['title']) + " --- http://reddit.com" + str(t['data']['permalink']))
                        time.sleep(5)

                    self.seen_threads.append(t['data']['id'])
                    with open(self.seenFile, 'w') as fh:
                        pickle.dump(self.seen_threads, fh)
    	except:
           #Fuck it.  Try again later.  whatever.
           pass
                    
    def login(self):
        log.info('logging in as '+config.get('reddit','username')+'.')
        
        req = self.session.post('http://www.reddit.com/api/login/'+config.get('reddit','username')+'', 
            data={'user':config.get('reddit','username'), 'passwd':config.get('reddit', 'password'), 'api_type':'json'}
        )

        obj = json.loads(req.text)
        if (len(obj['json']['errors']) == 0):
            self.cookie = obj['json']['data']['cookie']
            self.session.modhash = obj['json']['data']['modhash']
        else:
            raise Exception('Invalid login')

