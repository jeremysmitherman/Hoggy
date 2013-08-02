from sqlalchemy import create_engine, MetaData, Table, Column, Integer,String, Float
import os
import ConfigParser

try:
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
except ConfigParser.NoSectionError:
    print "Config file is un-readable or not present.  Make sure you've created a config.ini (see config.ini.default for an example)"
    exit()

    
if config.get('db', 'type') == 'mysql':
    MSQLUname = config.get('db', 'mysqlusername')
    MSQLPW = config.get('db', 'mysqlpassword')
    MSQLHost = config.get('db', 'mysqlhost')
    MSQLPort = config.get('db', 'mysqlport')
    MSQLDB = config.get('db', 'mysqldatabase')
    engine = create_engine('mysql://%s:%s@%s:%s/%s' % (MSQLUname, MSQLPW, MSQLHost, MSQLPort, MSQLDB))
else:
    HERE = os.path.dirname(os.path.abspath(__file__))
    SQLITEFILE = config.get('db', 'file')
    engine = create_engine('sqlite:///%s/%s' % (HERE, SQLITEFILE))

metadata = MetaData(engine)

quotes = Table('quotes', metadata,
    Column('id', Integer, primary_key=True),
    Column('body', String(200))
)
times = Table('times', metadata,
    Column('name', String(20), primary_key=True),
    Column('time', Float)
)
feeds = Table('feeds', metadata, 
    Column('id', Integer, primary_key=True),
    Column('url', String(200))
)
seen_feeds = Table('seen_feeds', metadata,
    Column('story_url',primary_key=True),
    Column('feed_id', Integer, Foreign_key("feeds.id"))
)
if __name__ == '__main__':
    quotes.create()
    times.create()
    feeds.create()
    print "Database setup completed successfully."
