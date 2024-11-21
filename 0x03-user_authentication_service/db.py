#!/usr/bin/env python3
"""
Flask app
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

from user import Base, User


class DB:
    """
    DB class for handling database operations.
    """

    def __init__(self) -> None:
        """Initialize the database connection and create tables."""
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Lazy-load the session object for interacting with the database."""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Adds a new user to the database.

        Args:
            email (str): The email address of the user.
            hashed_password (str): The hashed password of the user.

        Returns:
            User: The user object that was added to the database.
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """
        Finds a user by arbitrary keyword arguments.

        Args:
            kwargs: Arbitrary keyword arguments to filter users.

        Returns:
            User: The user found in the database.

        Raises:
            NoResultFound: If no user matches the query.
            ValueError: If an invalid attribute is provided.
        """
        all_users = self._session.query(User)
        for key, value in kwargs.items():
            if not hasattr(User, key):
                raise ValueError(f"user not founde: {key}")
            all_users = all_users.filter(getattr(User, key) == value)

        try:
            return all_users.first()
        except NoResultFound:
            raise NoResultFound(f"No user found matching {kwargs}")

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update User details.
        Args:
            user_id (int): The ID of the user to update.
            kwargs: Arbitrary keyword arguments to update the user attributes.
        Raises:
            ValueError: If no user with the given ID is found, or if
                        an invalid attribute is provided.
        """
        user = self.find_user_by(id=user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found")

        for key, value in kwargs.keys():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise ValueError(f"Invalid attribute: {key}")
        self._session.commit()

    def close(self):
        """Close the database session."""
        if self.__session:
            self.__session.close()
