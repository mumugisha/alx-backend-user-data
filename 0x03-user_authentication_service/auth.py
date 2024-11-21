#!/usr/bin/env python3
"""Authentication of API."""

import bcrypt
from uuid import uuid4
from sqlalchemy.exc import NoResultFound
from typing import TypeVar, Union
from db import DB
from user import User

U = TypeVar("User")


def _hash_password(password: str) -> bytes:
    """
    Hash a password and return bytes.

    Args:
        password (str): Password in string format.

    Returns:
        bytes: Hashed password.
    """
    encoded_pwd = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(encoded_pwd, salt)
    return hashed_pwd


def _generate_uuid() -> str:
    """
    Generate a UUID and return it as a string.

    Returns:
        str: UUID string.
    """
    return str(uuid4())


class Auth:
    """
    Class to manage API authentication.
    """

    def __init__(self) -> None:
        """
        Initialize Authentication.
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Register a new user and return the user object.

        Args:
            email (str): New user's email.
            password (str): New user's password.

        Returns:
            User: Newly created user if no user with email exists.

        Raises:
            ValueError: If a user with the given email already exists.
        """
        try:
            existing_usr = self._db.find_user_by(email=email)
            if existing_usr:
                raise ValueError(f"User {email} already exists")
        except NoResultFound:
            pass

        hashed_pwd = _hash_password(password)
        new_user = self._db.add_user(
            email=email, hashed_password=hashed_pwd.decode("utf-8")
        )
        return new_user

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validate user login credentials.

        Args:
            email (str): User email address.
            password (str): User password.

        Returns:
            bool: True if credentials are correct, else False.
        """
        try:
            existing_user = self._db.find_user_by(email=email)
            if existing_user:
                encoded_pwd = password.encode()
                hashed_pwd = existing_user.hashed_password.encode("utf-8")
                return bcrypt.checkpw(encoded_pwd, hashed_pwd)
            return False
        except NoResultFound:
            return False

    def create_session(self, email: str) -> Union[None, str]:
        """
        Create a session ID for an existing user.

        Args:
            email (str): User's email address.

        Returns:
            Union[None, str]: Session ID or None.
        """
        try:
            existing_user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(existing_user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> Union[None, U]:
        """
        Get a user from a session ID.

        Args:
            session_id (str): Session ID.

        Returns:
            Union[None, User]: User object if exists, else None.
        """
        try:
            existing_user = self._db.find_user_by(session_id=session_id)
            return existing_user
        except Exception:
            return None

    def destroy_session(self, user_id: int) -> None:
        """
        Destroy a user's session by setting session_id to None.

        Args:
            user_id (int): User ID.

        Returns:
            None
        """
        try:
            user = self._db.find_user_by(id=user_id)
            user.session_id = None
            self._db._session.commit()
        except Exception:
            pass

    def get_reset_password_token(self, email: str) -> str:
        """
        Generate a reset password token for a user.

        Args:
            email (str): User's email.

        Returns:
            str: Generated reset token.

        Raises:
            ValueError: If user with given email does not exist.
        """
        try:
            existing_user = self._db.find_user_by(email=email)
            token = _generate_uuid()
            self._db.update_user(existing_user.id, reset_token=token)
            return token
        except Exception:
            raise ValueError()

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Update a user's password.

        Args:
            reset_token (str): Reset token issued to reset a password.
            password (str): New password.

        Returns:
            None

        Raises:
            ValueError: If reset token is invalid.
        """
        try:
            existing_user = self._db.find_user_by(reset_token=reset_token)
        except Exception:
            raise ValueError()

        hashed_pwd = _hash_password(password)
        self._db.update_user(
            existing_user.id, hashed_password=hashed_pwd.decode("utf-8")
        )
        self._db.update_user(existing_user.id, reset_token=None)


if __name__ == "__main__":
    pass
