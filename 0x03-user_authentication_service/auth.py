#!/usr/bin/env python3
""" Authentication of API """

import bcrypt
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound
from typing import TypeVar, Union
from db import DB
from user import User

U = TypeVar('User')


def _hash_password(password: str) -> bytes:
    """
    Hashed password to return bytes.
    Args:
        password (str): password in string format
    """
    pwd = password.encode('utf-8')
    return bcrypt.hashpw(pwd, bcrypt.gensalt())


def _generate_uuid() -> str:
    """
    Generate a uuid and return as string.
    """
    return str(uuid4())


class Auth:
    """
    Class to manage API authentication.
    """
    def __init__(self) -> None:
        self.db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Register a new user and return user object.
        Args:
            email (str): new user email
            password (str): new user password
        Return:
            The newly created user if no user with the email exists,
            else raise ValueError.
        """
        try:
            self.db.find_user_by(email=email)
        except NoResultFound:
            hash = _hash_password(password)
            user = self.db.add_user(email, hash)
            return user
        raise ValueError(f"User {email} already exists")

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validate user login credentials.
        Args:
            email (str): user email address
            password (str): user password
        Return:
            True if credentials are correct, else False.
        """
        try:
            user = self.db.find_user_by(email=email)
        except NoResultFound:
            return False

        usr_pwd = user.hashed_password
        passd = password.encode("utf-8")
        return bcrypt.checkpw(passd, usr_pwd)

    def create_session(self, email: str) -> Union[None, str]:
        """
        Create a session_id for an existing user and update their session_id.
        Args:
            email (str): user email address
        Return:
            The session_id or None if user does not exist.
        """
        try:
            user = self.db.find_user_by(email=email)
        except NoResultFound:
            return None

        session_id = _generate_uuid()
        self.db.update_user(user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[None, U]:
        """
        Retrieve the user corresponding to a session_id.
        Args:
            session_id (str): session ID
        Return:
            User object if found, else None.
        """
        if session_id is None:
            return None

        try:
            user = self.db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

        return user

    def destroy_session(self, user_id: int) -> None:
        """
        Destroy a user's session by setting session_id to None.
        Args:
            user_id (int): user ID
        Return:
            None
        """
        try:
            self.db.update_user(user_id, session_id=None)
        except ValueError:
            return None

    def get_reset_password_token(self, email: str) -> str:
        """
        Generate a reset token for a user identified by their email.
        Args:
            email (str): user's email address
        Return:
            Newly generated reset token.
        """
        try:
            user = self.db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError

        reset_token = _generate_uuid()
        self.db.update_user(user.id, reset_token=reset_token)
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Update a user's password using their reset token.
        Args:
            reset_token (str): reset token issued to reset password
            password (str): new password
        Return:
            None
        """
        try:
            user = self.db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError

        hashed = _hash_password(password)
        self.db.update_user(
            user.id, hashed_password=hashed, reset_token=None)
