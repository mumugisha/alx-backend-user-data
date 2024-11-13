#!/usr/bin/env python3
""" Authentication of API """

from flask import request
from typing import List, TypeVar


class Auth:
    """
    Class to manage API authentication
    """
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """
        Determines if authentication is required for a given path.

        Args:
            path (str): The path to check.
            excluded_paths (List[str]): List of paths that do not
                                        require authentication.

        Returns:
            bool: True if authentication is required, False otherwise.
        """
        if path is None:
            return True
        elif excluded_paths is None or excluded_paths == []:
            return True
        elif path in excluded_paths:
            return False
        else:
            for i in excluded_paths:
                if i.startswith(path) or path.startswith(i):
                    return False
                if i[-1] == "*":
                    if path.startswith(i[:-1]):
                        return False
        return True

    def authorization_header(self, request=None) -> str:
        """
        Returns the authorization header from the request.

        Args:
            request: The Flask request object.

        Returns:
            str: The authorization header, or None if not present.
        """
        if request is None:
            return None
        header = request.headers.get('Authorization')
        return header

    def current_user(self, request=None) -> TypeVar('User'):
        """
        Returns the user information from the request.

        Args:
            request: The Flask request object.

        Returns:
            TypeVar('User'): The user, or None if not found.
        """
        return None
