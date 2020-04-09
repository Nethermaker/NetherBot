import os
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()
DATABASE_ENDPOINT = os.getenv('DATABASE_ENDPOINT')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

Persisted = declarative_base()


class User(Persisted):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(BigInteger, nullable=False)
    bng_profile_id = Column(String(256))


class NetherbotDatabase(object):
    url = f'mysql+pymysql://admin:{DATABASE_PASSWORD}@{DATABASE_ENDPOINT}:3306/netherbot'

    def __init__(self):
        self.engine = create_engine(self.url)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

    def ensure_tables_exist(self):
        Persisted.metadata.create_all(self.engine)

    def create_session(self):
        return self.Session()


def setup_database():
    netherbot_db = NetherbotDatabase()
    netherbot_db.ensure_tables_exist()
    print('Tables Created')
    session = netherbot_db.create_session()
    # Can add starter data here
    session.commit()


if __name__ == '__main__':
    connection_string = f'mysql+pymysql://admin:{DATABASE_PASSWORD}@{DATABASE_ENDPOINT}:3306/netherbot'
    print(connection_string)
    engine = create_engine(connection_string, echo=False)
    print(engine.table_names())
    # setup_database()
    print(engine.table_names())
