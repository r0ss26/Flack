from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), index=True, primary_key = True, nullable = False)
    username = Column(String(), nullable = False)
    hash = Column(String(), nullable = False)

class Channels(Base):
    __tablename__ = 'channels'
    channel = Column(String(), primary_key = True, nullable = False)

class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer(), index=True, primary_key = True, nullable = False)
    user_id = Column(Integer(), index=True, primary_key = True, nullable = False)
    channel = Column(String(), nullable = False)
    message = Column(String(), nullable = False)
