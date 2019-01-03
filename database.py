# This module initializes the database

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(os.environ.get('DATABASE_URL'), echo=True, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                        autoflush=True,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from models import Base, User, Channel, Message
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()