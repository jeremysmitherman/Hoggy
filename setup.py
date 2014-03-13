from sqlalchemy import create_engine, MetaData, Table, Column, Integer,String, Float, DateTime
import os, sys
import ConfigParser

try:
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])
except:
    config.read(os.path.dirname(os.path.abspath(__file__)) + "/config.ini")


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
    Column('story_url',String(200), primary_key=True)
)

#SCHEMA (id int, text object, text relation, text adder, timestamp added)
# This is used by !learn and !what
learn = Table('learn', metadata,
    Column('id', Integer, primary_key =True),
    Column('key', String(100)),
    Column('relation', String(200)),
    Column('added', String(32)),
    Column('timestamp', DateTime)
)


def _create_tables(tables):
    for table in tables:
        try:
            table.create()
            print "Created %s" % table
        except:
            # Probably already made
            pass

if __name__ == '__main__':
    _create_tables([quotes, times, feeds, seen_feeds, learn])
    print "Database setup completed successfully."
