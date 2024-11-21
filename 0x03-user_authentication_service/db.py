#!/usr/bin/env python3
"""
DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError

from user import Base, User


class DB:
    """DB class"""

    def __init__(self) -> None:
        """Initialize a new DB instance."""
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object."""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Create a User and save it to the database.

        Args:
            email (str): User email.
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
        Find a user by arbitrary attributes.

        Args:
            kwargs (dict): A dictionary of attributes.

        Returns:
            User: User object matching the attributes.

        Raises:
            InvalidRequestError: If an attribute is invalid.
            NoResultFound: If no user matches the attributes.
        """
        for key in kwargs.keys():
            if not hasattr(User, key):
                raise InvalidRequestError(f"Invalid attribute: {key}")

        user = self._session.query(User).filter_by(**kwargs).first()
        if user:
            return user

        raise NoResultFound("No user found matching the given criteria.")

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user's attributes in the database.

        Args:
            user_id (int): ID of the user to update.
            kwargs (dict): Dictionary of key-value pairs of attributes.

        Raises:
            ValueError: If user is not found or an attribute is invalid.

        Returns:
            None
        """
        try:
            user_updated = self.find_user_by(id=user_id)
        except NoResultFound:
            raise ValueError("User not found.")

        for attr, value in kwargs.items():
            if hasattr(User, attr):
                setattr(user_updated, attr, value)
            else:
                raise ValueError(f"Invalid attribute: {attr}")
        self._session.commit()


if __name__ == "__main__":
    my_db = DB()

    user = my_db.add_user("test@test.com", "PwdHashed")
    print(user.id)

    find_user = my_db.find_user_by(email="test@test.com")
    print(find_user.id)

    try:
        find_user = my_db.find_user_by(email="test@test.com")
        print(find_user.id)
    except NoResultFound:
        print("Not found")

    try:
        find_user = my_db.find_user_by(email="test@test.com")
        print(find_user.id)
    except InvalidRequestError:
        print("Invalid attribute")
