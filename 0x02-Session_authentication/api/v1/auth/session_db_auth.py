#!/usr/bin/env python3
"""Authentication of API."""

from .session_exp_auth import SessionExpAuth
from models.user_session import UserSession


class SessionDBAuth(SessionExpAuth):
    """Defined SessionDBAuth Class."""

    def create_session(self, user_id=None):
        """
        Create a session ID.

        Args:
            user_id (str): User ID.

        Returns:
            str: Session ID or None if creation fails.
        """
        session_id = super().create_session(user_id)
        if not session_id:
            return None
        kw = {
            "user_id": user_id,
            "session_id": session_id
        }
        user = UserSession(**kw)
        user.save()
        return session_id

    def user_id_for_session_id(self, session_id=None):
        """
        Return user ID using session ID.

        Args:
            session_id (str): Session ID.

        Returns:
            str: User ID or None if session ID is invalid.
        """
        user_id = UserSession.search({"session_id": session_id})
        if user_id:
            return user_id
        return None

    def destroy_session(self, request=None):
        """
        Delete user session.

        Args:
            request (flask.Request): The request object.

        Returns:
            bool: True if session was deleted, False otherwise.
        """
        if request is None:
            return False
        session_id = self.session_cookie(request)
        if not session_id:
            return False
        user_session = UserSession.search({"session_id": session_id})
        if user_session:
            user_session[0].remove()
            return True
        return False
