#!/usr/bin/env python3
"""
Declaring SQLAlchemy named User model.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    Define the User class for the 'users' table in the database.
    
    Attributes:
        id (int): The primary key for the user.
        name (str): The name of the user.
        hashed_password (str): The user's hashed password.
        session_id (str, optional): The session ID for the user, if any.
        reset_token (str, optional): The reset token for the user, if any.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250), nullable=True)
    reset_token = Column(String(250), nullable=True)
