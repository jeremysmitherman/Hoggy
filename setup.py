from sqlalchemy import create_engine, MetaData, Table, Column, Integer,String, Float
import os

HERE = os.path.dirname(os.path.abspath(__file__))
engine = create_engine('sqlite:///%s/hoggit.sqlite' % HERE)

metadata = MetaData(engine)

quotes = Table('quotes', metadata,
    Column('id', Integer, primary_key=True),
    Column('body', String(200))
)
times = Table('times', metadata,
    Column('name', String(20), primary_key=True),
    Column('time', Float)
)

if __name__ == '__main__':
    quotes.create()
    times.create()
