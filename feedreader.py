import threading
import feedparser


class FeedReader(threading.Thread):

	def __init__(self, in_queue, out_queue):
		self.in_queue = in_queue
		self.out_queue = out_queue
		threading.Thread.__init__(self)

	#Will return a list of any new entries in the given feed.
	def run(self):
		while(True):
			entries = []
			url = get_url() #Blocking until available on in_queue
			feed = feedparser.parse(url)
			for item in feed["items"]:
				entry = {"feed":feed["channel"]["title"],"title":item["title"], "url":item["link"]}
				entries.append(entry)

			self.out_queue.put(entries)

	#Read a url from the in_queue
	def get_url(self):
		return in_queue.get()

class FeedChecker(threading.Thread):
	from setup import seen_feeds
	def __init__(self,feed,client,channel):
		self.client = client
		self.feed = feed
		self.channel = channel

	def run(self):
		check_seen(self.feed)

	def check_seen(self,feed):
		for article in feed:
			rs = seen_feeds.select(columns='url').execute().fetchall()
			if article["url"] in rs:
				continue
			#If it's not in the db, add it and spew it to channel.
			self.client.msg(self.channel,"%s: %s - %s".format(article["feed"],article["title"],article["url"]))

class FeedReaderManager():
	import ConfigParser
	from Queue import Queue, Empty
	config = ConfigParser.RawConfigParser()
	config.read('config.ini')
	from setup import feeds
	import datetime
	def __init__(self, client,channel):
		minutes = config.get('RSS','frequency')
		self.frequency = datetime.timedelta(minutes=minutes)
		self.max_thread_number = config.get('RSS','max_threads')
		self.url_queue = Queue()
		self.response_queue = Queue()
		self.client = client

	def begin(self):
		#Create the threads
		for _ in range(self.max_thread_number):
			get_thread().start()

	def run(self):
		while (True):
			now = datetime.datetime.now()
			next_update = now + self.frequency
			queue_feeds()
			while (True):
				try:
					sec_till_update = next_update - datetime.datetime.now() 
					feed = get_feed_from_queue(sec_till_update)
				except Empty:
					break

	def get_feed_from_queue(self,timeout):
		return self.response_queue.get(timeout=timeout)

	def queue_feeds(self):
		feed_list = get_feed_urls()
		for feed in feeds:
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

