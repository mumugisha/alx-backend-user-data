#!/usr/bin/env python3
"""
A module that provides functions to hash a password and validate it.
"""
import bcrypt
from bcrypt import hashpw


def hash_password(password: str) -> bytes:
    """
    Hashes a password using bcrypt and returns the hashed password.

    Args:
        password (str): The password to hash.

    Returns:
        bytes: The hashed password.
    """
    b = password.encode()
    hashed = hashpw(b, bcrypt.gensalt())
    return hashed


def is_valid(hashed_psw: bytes, password: str) -> bool:
    """
    Validates a password against a hashed password.

    Args:
        hashed_psw (bytes): The hashed password.
        password (str): The plain password to validate.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return bcrypt.checkpw(password.encode(), hashed_password)
