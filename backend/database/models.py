from sqlalchemy import Column, String, Integer, DateTime
from .database import Base

class UserInfo(Base):
    __tablename__ = "userinfo"

    userID = Column("userID", Integer, primary_key=True, autoincrement=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    user_class = Column("class", String(255), nullable=False)

class Apply(Base):
    __tablename__ = "apply"

    applyID = Column(Integer, primary_key=True, index=True)
    userID = Column(Integer, nullable=False)
    username = Column(String(255), nullable=False)
    result = Column(Integer, default=0) 

class SystemLog(Base):
    __tablename__ = "systemlog"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userID = Column("userID", Integer, nullable=False)
    username = Column(String(255), nullable=False)
    logtype = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=True) 