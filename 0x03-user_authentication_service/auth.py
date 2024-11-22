#!/usr/bin/env python3
"""Authentication of API."""

import bcrypt
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound
from typing import Union
import logging

from db import DB
from user import User

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Auth")


def _hash_password(password: str) -> bytes:
    """
    Hash a password and return bytes.
    Args:
        password (str): Password in string format.
    Returns:
        bytes: Hashed password.
    """
    pwd = password.encode("utf-8")
    return bcrypt.hashpw(pwd, bcrypt.gensalt())


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
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Register a new user and return the user object.

        Args:
            email (str): New user's email.
            password (str): New user's password.

        Returns:
            User: The newly registered user object.

        Raises:
            ValueError: If a user with the given email already exists.
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            hashed_password = _hash_password(password)
            user = self._db.add_user(email, hashed_password)
            logger.info(f"User {email} registered successfully")
            return user

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
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False
        pwd_hash = user.hashed_password
        return bcrypt.checkpw(password.encode("utf-8"), pwd_hash)

    def create_session(self, email: str) -> Union[None, str]:
        """
        Create a session ID for an existing user.
        Args:
            email (str): User's email address.
        Returns:
            Union[None, str]: Session ID or None.
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            logger.info(f"Session created for user: {email}")
            return session_id
        except NoResultFound:
            logger.warning(f"Session creation failed for email: {email}")
            return None

    def get_user_from_session_id(self, session_id: str) -> Union[None, User]:
        """
        Get a user from a session ID.
        Args:
            session_id (str): Session ID.
        Returns:
            Union[None, User]: User object if exists, else None.
        """
        if session_id is None:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """
        Destroy a user's session by setting session_id to None.
        Args:
            user_id (int): User ID.
        Raises:
            ValueError: If user ID is invalid.
        """
        try:
            self._db.update_user(user_id, session_id=None)
            logger.info(f"Session destroyed for user_id: {user_id}")
        except ValueError as e:
            raise ValueError(f"Failed to destroy session: {e}")

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
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError(f"User with email {email} not found")

        reset_token = _generate_uuid()
        self._db.update_user(user.id, reset_token=reset_token)
        logger.info(f"Password reset token generated for user: {email}")
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Update a user's password.
        Args:
            reset_token (str): Reset token issued to reset a password.
            password (str): New password.
        Raises:
            ValueError: If reset token is invalid.
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError("Invalid reset token")

        hashed = _hash_password(password)
        self._db.update_user(
            user.id, hashed_password=hashed, reset_token=None
        )
        logger.info(
                f"Password updated for user with reset token: {reset_token}"
                )
