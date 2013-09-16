import cherrypy, ConfigParser, sys, logging, os
from setup import quotes, times, engine, feeds
from jinja2 import Environment, FileSystemLoader
import re

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8080,
                       })

env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')))

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

_urlfinderregex = re.compile(r'http([^\.\s]+\.[^\.\s]*)+[^\.\s]{2,}')

def linkify(text, maxlinklength = 100):
    def replacewithlink(matchobj):
        url = matchobj.group(0)
        text = unicode(url)
        if text.startswith('http://'):
            text = text.replace('http://', '', 1)
        elif text.startswith('https://'):
            text = text.replace('https://', '', 1)

        if text.startswith('www.'):
            text = text.replace('www.', '', 1)

        if len(text) > maxlinklength:
            halflength = maxlinklength / 2
            text = text[0:halflength] + '...' + text[len(text) - halflength:]

        return '<a class="comurl" href="' + url + '" target="_blank" rel="nofollow">' + text + '</a>'

    if text != None and text != '':
        return _urlfinderregex.sub(replacewithlink, text)
    else:
        return ''


class quoteSearch(object):
    def index(self, search = None):
        if search:
            q = quotes.select().order_by('id').where('body LIKE "%{0}%"'.format(search))
        else:
            q = quotes.select().order_by('id')
        rs = q.execute()
        rows = rs.fetchall()
        to_ret = []

        for r in rows:
            to_ret.append((r[0], linkify(r[1])))

        template = env.get_template("search.jinja2")
        return template.render(results=to_ret)
    index.exposed = True


if __name__ == "__main__":  
    cherrypy.quickstart(quoteSearch())
