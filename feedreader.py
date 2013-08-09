import threading
import feedparser
import ConfigParser
from Queue import Queue, Empty
from setup import feeds, seen_feeds
import datetime
from os import sys

feedparser.USER_AGENT = "RSS Feedparser for HoggyBot by /u/acidictadpole for /r/hoggit"

class FeedReader(threading.Thread):

	def __init__(self, in_queue, out_queue):
		self.in_queue = in_queue
		self.out_queue = out_queue
		self.stop = False
		threading.Thread.__init__(self)
		self.daemon = True

	#Will return a list of any new entries in the given feed.
	def run(self):
		while(True):
			entries = []
			url = self.get_url() #Blocking until available on in_queue
			feed = feedparser.parse(url)
			for item in feed["items"]:
				try:
					entry = {"feed":feed["channel"]["title"],"title":item["title"], "url":item["link"]}
					entries.append(entry)
				except:
					pass

			self.out_queue.put(entries)

	#Read a url from the in_queue
	def get_url(self):
		while (True):
			if (self.stop):
				sys.exit(0)
			try:
				return self.in_queue.get(timeout=5)
			except Empty:
				pass

	def send_stop(self):
		self.stop = True

class FeedChecker(threading.Thread):
	
	def __init__(self,feed,client,channel):
		self.client = client
		self.feed = feed
		self.channel = channel
		threading.Thread.__init__(self)
		self.daemon = True

	def run(self):
		try:
		    self.check_seen(self.feed)
		except:
			pass

	def check_seen(self,feed):
		rs = seen_feeds.select().execute().fetchall()
		for article in feed:
			for seen_feed in rs:
				if article["url"] in seen_feed["story_url"]:
					return
			#If it's not in the db, add it and spew it to channel.
			message = "%s: %s - %s" % (article["feed"],article["title"],article["url"])
			message = message.encode('ascii', 'ignore')
			self.client.msg(self.channel, message)
			self.add_feed_to_seen(article['url'])

	def add_feed_to_seen(self,url):
		query = seen_feeds.insert()
		query.execute(story_url=url)

class FeedReaderManager(threading.Thread):
	
	def __init__(self, client,channel):
		self.config = ConfigParser.RawConfigParser()
		self.config.read(sys.argv[1])
		minutes = self.config.get('RSS','frequency')
		self.frequency = datetime.timedelta(minutes=float(minutes))
		self.max_thread_number = self.config.get('RSS','max_threads')
		self.url_queue = Queue()
		self.response_queue = Queue()
		self.client = client
		self.channel = channel
		self.threads = []
		threading.Thread.__init__(self)
		self.daemon = True

	def begin(self):
		#Create the threads
		i = 0
		for _ in range(int(self.max_thread_number)):
			thread = self.get_thread()
			try:
				thread.setName(str(i))
				i +=1 
				thread.start() 
				self.threads.append(thread)
			except:
				sys.exit(0)

	def check_threads(self):
		for thread in self.threads:
			if not thread.is_alive():
				thread.start()

	def run(self):
		while (True):
			print "Running"
			now = datetime.datetime.now()
			next_update = now + self.frequency
			self.queue_feeds()
			while (True):
				try:
					sec_till_update = (next_update - datetime.datetime.now()).seconds
					feed = self.get_feed_from_queue(sec_till_update)
					self.check_threads()
					feedChecker = FeedChecker(feed,self.client,self.channel)
					feedChecker.start()
				except Empty:
					break
				except KeyboardInterrupt:
					self.clean_threads()
					raise
				except ValueError:
					break

	def clean_threads(self):
		for thread in self.threads:
			thread.send_stop()

	def get_feed_from_queue(self,timeout):
		return self.response_queue.get(timeout=timeout)

	def queue_feeds(self):
		feed_list = self.get_feed_urls()
		for feed in feed_list:
			self.url_queue.put(feed)

	#Get a list of urls from the database.
	def get_feed_urls(self):
		feed_list = feeds.select().execute().fetchall()
		feed_urls = []
		for feed in feed_list:
			feed_urls.append(feed["url"])

		return feed_urls


	def get_thread(self):
		return FeedReader(self.url_queue, self.response_queue)
