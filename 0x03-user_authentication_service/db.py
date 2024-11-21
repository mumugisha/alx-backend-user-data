#!/usr/bin/env python3
"""
Flask app
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from user import Base, User


class DB:
    """
    DB class
    """

    def __init__(self) -> None:
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        all_users = self._session.query(User)
        for key, value in kwargs.items():
            if key not in User.__dict__:
                raise ValueError("Invalid attribute")
            all_users = all_users.filter(getattr(User, key) == value)
        try:
            return all_users.one()
        except Exception:
            raise ValueError()

    def update_user(self, user_id: int, **kwargs) -> None:
        try:
            usr = self.find_user_by(id=user_id)
        except ValueError:
            raise ValueError()
        for key, value in kwargs.items():
            if hasattr(usr, key):
                setattr(usr, key, value)
            else:
                raise ValueError
        self._session.commit()
