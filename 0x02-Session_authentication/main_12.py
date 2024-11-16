#!/usr/bin/python3
""" Check response
"""
from time import sleep
import sys


if __name__ == "__main__":
    try:
        from api.v1.auth.session_exp_auth import SessionExpAuth
        sea = SessionExpAuth()
        user_id = "User1"
        session_id = sea.create_session(user_id)
        if session_id is None:
            print("create_session should return a Session ID if user_id is "
                  "valid")
            sys.exit(1)

        sleep(2)

        user_id_r = sea.user_id_for_session_id(session_id)
        if user_id_r is None:
            print("user_id_for_session_id should return the User ID linked "
                  "to the Session ID")
            sys.exit(1)
        if user_id_r != user_id:
            print("user_id_for_session_id should return the User ID linked "
                  "to the Session ID")
            sys.exit(1)

        print("OK", end="")
    except Exception as e:
        print(f"Error: {e}")
