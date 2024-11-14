#!/usr/bin/env python3
""" Authentication of API """

import os
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
            bool: True if path is not in excluded_paths, False otherwise.
        """
        if path is None:
            return True
        elif not excluded_paths:
            return True
        elif path in excluded_paths:
            return False
        else:
            for i in excluded_paths:
                if i.startswith(path) or path.startswith(i):
                    return False
                if i.endswith("*") and path.startswith(i[:-1]):
                    return False
        return True

    def authorization_header(self, request=None) -> str:
        """
        Returns the authorization header from the request.

        Args:
            request (Request, optional): The request object.

        Returns:
            str: The value of the Authorization header if present, None otherwise.
        """
        if request is None:
            return None
        header = request.headers.get('Authorization')
        if header is None:
            return None
        return header

    def current_user(self, request=None) -> TypeVar('User'):
        """
        Returns the user information from the request.

        Args:
            request (Request, optional): The request object.

        Returns:
            User: The current user if available, None otherwise.
        """
        return None

    def session_cookie(self, request=None):
        """
        Returns the session cookie from the user request.

        Args:
            request (Request, optional): The request object.

        Returns:
            str: The value of the session cookie if available, None otherwise.
        """
        if request is None:
            return None
        session_name = os.getenv('SESSION_NAME')
        return request.cookies.get(session_name)
