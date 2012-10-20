import requests
import threading
import json
import pickle
import logging
import time
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.ini')

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
    new_url = 'http://www.reddit.com/r/hoggit/new.json'
    stop_event = threading.Event()
    
    def __init__(self, client, channel):
        log.info('INIT RedditUpdateThread...')
        threading.Thread.__init__(self)
        self.daemon = True
        self.isRunning = True
        self.client = client
        self.channel = channel
        log.debug('RedditUpdateThread set to channel %s', self.channel)

        log.info('Loading seen threads...')
        try:
            with open('seen_threads.dat') as seen_threads_file:
                self.seen_threads = pickle.load(seen_threads_file)
        except IOError:
            log.debug('seen_threads.dat either doesn\'t exist or is non-editable.  Creating new seen_threads.dat')
            self.seen_threads = []
            open('seen_threads.dat', 'w').close()
        
        except EOFError:
            log.debug('seen_threads exists but is empty.  Continuing...')
            self.seen_threads = []

        log.info('Loaded %d seen threads.', len(self.seen_threads))

    def run(self):
        log.info('logging in as zellyman...')
        self.session = requests.session()
        req = self.session.post('http://www.reddit.com/api/login/zellyman', 
            data={'user':config.get('reddit','username'), 'passwd':config.get('reddit', 'password'), 'api_type':'json'}
        )

        obj = json.loads(req.text)
        if (len(obj['json']['errors']) == 0):
            self.cookie = obj['json']['data']['cookie']
            self.session.modhash = obj['json']['data']['modhash']
        else:
            raise Exception('Invalid login')

        log.info('Starting main loop')
        while self.isRunning:
            log.debug('Enter main loop...')
            log.debug('Requesting new threads...')
            headers = {"User-Agent":"New Thread updater.  /u/zellyman for /r/hoggit"}
            req = self.session.get(self.new_url, headers=headers)
            if req.status_code != 200:
                log.info('Failed getting new threads.')
            else:
                data = json.loads(req.text)
                threads = data['data']['children']
                for t in threads:
                    if t['data']['id'] not in self.seen_threads:
                        self.client.msg(self.channel, "NEW THREAD BY " + str(t['data']['author'])  + ": " + str(t['data']['title']) + " --- http://reddit.com" + str(t['data']['permalink']))
                        self.seen_threads.append(t['data']['id'])
                        with open('seen_threads.dat', 'w') as fh:
                            pickle.dump(self.seen_threads, fh)
                        time.sleep(5)
            if self.stop_event.wait(30) == True:
                self.isRunning = False
            
        log.info('Left main loop.')
