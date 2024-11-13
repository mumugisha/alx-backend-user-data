#!/usr/bin/env python3
"""Authentication of API."""

import base64
from .auth import Auth
from uuid import uuid4
from typing import TypeVar
from models.user import User


class SessionAuth(Auth):
    """Authorization protocol implementation."""

    user_id_session_id = {}

    def create_session(self, user_id: str = None) -> str:
        """
        Function to create a session ID.

        Args:
            user_id (str): User ID.

        Returns:
            str: The session ID, or None if user_id is invalid.
        """
        if user_id is None or not isinstance(user_id, str):
            return None
        session_id = str(uuid4())
        self.user_id_session_id[session_id] = user_id
        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """
        Returns user ID using session ID.

        Args:
            session_id (str): Session ID.

        Returns:
            str: User ID or None if session_id is None or not a string.
        """
        if session_id is None or not isinstance(session_id, str):
            return None
        return self.user_id_session_id.get(session_id)

    def current_user(self, request=None):
        """
        Return user instance.

        Args:
            request: Request object.

        Returns:
            User instance if session exists, otherwise None.
        """
        session_cookie = self.session_cookie(request)
        user_id = self.user_id_for_session_id(session_cookie)
        return User.get(user_id) if user_id else None

    def destroy_session(self, request=None) -> bool:
        """
        Delete user session.

        Args:
            request: Request object.

        Returns:
            bool: True if session was destroyed, False otherwise.
        """
        if request is None:
            return False
        session_cookie = self.session_cookie(request)
        if session_cookie is None:
            return False
        self.user_id_session_id.pop(session_cookie, None)
        return True
