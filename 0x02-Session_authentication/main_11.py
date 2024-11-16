#!/usr/bin/python3
""" Check response
"""
import requests
from time import sleep

if __name__ == "__main__":
    user_email = "u11@hbtn.io"
    user_pwd = "pwd11"

    r = requests.post(
        'http://0.0.0.0:3456/api/v1/auth_session/login',
        data={'email': user_email, 'password': user_pwd},
    )
    if r.status_code != 200:
        print("Wrong status code: {}".format(r.status_code))
        exit(1)
    if r.headers.get('content-type') != "application/json":
        print("Wrong content type: {}".format(r.headers.get('content-type')))
        exit(1)

    try:
        r_json = r.json()

        r_user_email = r_json.get('email')
        if r_user_email is None:
            print("User is not returned")
            exit(1)

        if r_user_email != user_email:
            print("User returned is not the same: {}".format(r_json))
            exit(1)
        user_id = r_json.get('id')

        cookie_session_id = r.cookies.get('_my_session_id')
        if cookie_session_id is None:
            print("No cookie _my_session_id returned")
            exit(1)

        sleep(1)

        """ Request Me """
        r_user_me = requests.get(
            'http://0.0.0.0:3456/api/v1/users/me',
            cookies={'_my_session_id': cookie_session_id},
        )
        if r_user_me.status_code != 200:
            print("Wrong status code: {}".format(r_user_me.status_code))
            exit(1)
        if r_user_me.headers.get('content-type') != "application/json":
            print(
                "Wrong content type: {}".format(r_user_me.headers.get(
                    'content-type'))
            )
            exit(1)

        r_user_me_json = r_user_me.json()

        r_user_me_id = r_user_me_json.get('id')
        if r_user_me_id is None:
            print("User is not returned")
            exit(1)

        if r_user_me_id != user_id:
            print("User returned is not the same: {}".format(r_user_me_json))
            exit(1)

        print("OK", end="")
    except Exception:  # Be specific with exception handling
        print("Error, not a JSON")
