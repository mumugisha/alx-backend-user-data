#!/usr/bin/env python3
"""Authentication of API with session expiration."""

import os
from datetime import datetime, timedelta
from .session_auth import SessionAuth


class SessionExpAuth(SessionAuth):
    """SessionExpAuth class with expiration date for sessions."""

    def __init__(self):
        """Initialize the SessionExpAuth class with session duration."""
        try:
            session_duration = int(os.getenv('SESSION_DURATION', 0))
        except ValueError:
            session_duration = 0
        self.session_duration = session_duration

    def create_session(self, user_id=None):
        """
        Create a session ID with an associated creation time.
        """
        session_id = super().create_session(user_id)
        if not session_id:
            return None
        session_dictionary = {
            "user_id": user_id,
            "created_at": datetime.now()
        }
        self.user_id_by_session_id[session_id] = session_dictionary
        return session_id

    def user_id_for_session_id(self, session_id=None):
        """
        Return the user ID associated with a valid session ID.
        """
        if not session_id:
            return None
        if session_id not in self.user_id_by_session_id.keys():
            return None

        session_dictionary = self.user_id_by_session_id.get(session_id)
        if not session_dictionary:
            return None

        if self.session_duration <= 0:
            return session_dictionary.get("user_id")

        created_at = session_dictionary.get("created_at")
        if not created_at:
            return None

        expired_time = created_at + timedelta(seconds=self.session_duration)
        if datetime.now() > expired_time:
            return None

        return session_dictionary.get("user_id")
