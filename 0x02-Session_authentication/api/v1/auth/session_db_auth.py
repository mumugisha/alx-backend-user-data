#!/usr/bin/env python3
"""Authentication of API."""

from .session_exp_auth import SessionExpAuth
from models.user_session import UserSession

class SessionDBAuth(SessionExpAuth):
    """Session-based authentication using a database-backed session."""

    def create_session(self, user_id=None):
        """
        Create and store a new session ID in the database.

        Args:
            user_id (str): The ID of the user.
        
        Returns:
            str: The session ID or None if the session could not be created.
        """
        session_id = super().create_session(user_id)
        if not session_id:
            return None

        # Store the session in the UserSession model
        user_session = UserSession(user_id=user_id, session_id=session_id)
        user_session.save()  # Save the session to the database
        return session_id

    def user_id_for_session_id(self, session_id=None):
        """
        Retrieve the user ID associated with a session ID.

        Args:
            session_id (str): The session ID.
        
        Returns:
            str: The user ID or None if the session ID is invalid.
        """
        user_sessions = UserSession.search({"session_id": session_id})
        if user_sessions:
            return user_sessions[0].user_id
        return None

    def destroy_session(self, request=None):
        """
        Destroy the session by removing the UserSession from the database.

        Args:
            request: The request object containing the session cookie.
        
        Returns:
            bool: True if the session was destroyed, False otherwise.
        """
        if request is None:
            return False
        
        # Get the session_id from the cookie
        session_id = self.session_cookie(request)
        if not session_id:
            return False

        # Find the user session and remove it
        user_sessions = UserSession.search({"session_id": session_id})
        if user_sessions:
            user_sessions[0].remove()
            return True
        return False
