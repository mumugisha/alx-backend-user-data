#!/usr/bin/env python3
"""Authentication of API."""

from models.base import Base


class UserSession(Base):
    """Class representing a user session for API authentication."""

    def __init__(self, *args: list, **kwargs: dict):
        """
        Initialize a UserSession instance.

        Args:
            args (list): Variable length argument list.
            kwargs (dict): Arbitrary keyword arguments that may include:
                - 'user_id' (str): The ID of the user associated session.
                - 'session_id' (str): The unique session ID.
        """
        super().__init__(*args, **kwargs)
        self.user_id: str = kwargs.get('user_id')
        self.session_id: str = kwargs.get('session_id')
