#!/usr/bin/env python3
"""
DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError

from user import Base, User


class DB:
    """DB class"""

    def __init__(self) -> None:
        """
        Initialize a new DB instance.
        """
        self._engine = create_engine(
            "sqlite:///a.db", echo=False
        )
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        Memoized session object.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Create a User object and save it to the database.

        Args:
            email (str): User's email address.
            hashed_password (str): Hashed password.

        Returns:
            User: Newly created User object.
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """
        Find a user by attributes.

        Args:
            **kwargs: Arbitrary keyword arguments representing attributes
                      to match the user.

        Returns:
            User: User object if a match is found.

        Raises:
            InvalidRequestError: If any attribute is invalid.
            NoResultFound: If no user matches the query.
        """
        all_users = self._session.query(User)
        for key, value in kwargs.items():
            if key not in User.__dict__:
                raise InvalidRequestError(
                    f"Invalid attribute: {key}"
                )
            for user in all_users:
                if getattr(user, key) == value:
                    return user
        raise NoResultFound(
            "No user found with the given attributes."
        )

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user's attributes.

        Args:
            user_id (int): User's ID.
            **kwargs: Key-value pairs representing attributes and new values.

        Raises:
            ValueError: If user does not exist or invalid attribute is passed.

        Returns:
            None
        """
        try:
            user = self.find_user_by(id=user_id)
        except NoResultFound:
            raise ValueError(
                f"No user found with ID {user_id}"
            )
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise ValueError(
                    f"Invalid attribute: {key}"
                )
        self._session.commit()
