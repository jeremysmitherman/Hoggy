from sqlalchemy import *
import os

HERE = os.path.dirname(os.path.abspath(__file__))
engine = create_engine('sqlite:///%s/hoggit.sqlite' % HERE)

metadata = MetaData(engine)

quotes = Table('quotes', metadata,
    Column('id', Integer, primary_key=True),
    Column('body', String(200))
)
if __name__ == '__main__':
	quotes.create()
