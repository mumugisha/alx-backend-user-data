#!/usr/bin/env python3
"""
Session ID, you can request all protected API
routes by using this Session ID
"""

from os import getenv
from flask import jsonify, request, abort
from api.v1.views import app_views
from models.user import User


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def auth_session():
    """
    Function that handles user login
    Return:
         dictionary representation of the user if found;
         otherwise, returns an error message.
    """
    email = request.form.get('email')
    password = request.form.get('password')
    if email is None or email == '':
        return jsonify({"error": "email missing"}), 400
    if password is None or password == '':
        return jsonify({"error": "password missing"}), 400
    users = User.search({"email": email})
    if not users or users == []:
        return jsonify({"error": "no user found for this email"}), 404
    for user in users:
        if user.is_valid_password(password):
            from api.v1.app import auth
            session_id = auth.create_session(user.id)
            resp = jsonify(user.to_json())
            session_name = getenv('SESSION_NAME')
            resp.set_cookie(session_name, session_id)
            return resp
    if not users:
        return jsonify({"error": "wrong password"}), 401


@app_views.route('/auth_session/logout', methods=['DELETE'],
                 strict_slashes=False)
def handle_logout():
    """
    Handles user logout and session destruction.
    Returns:
        - 200 if the session is successfully destroyed.
        - 404 if the session does not exist.
    """
    session_name = getenv('SESSION_NAME', '_my_session_id')
    session_id = request.cookies.get(session_name)

    if not session_id:
        print("No session ID found in cookies.")
        abort(404)

    # Debugging
    print(f"Attempting to destroy session with ID: {session_id}")

    from api.v1.app import auth
    if auth.destroy_session(request):
        print(f"Session {session_id} destroyed successfully.")
        return jsonify({}), 200
    else:
        print(f"Failed to destroy session {session_id}.")
        abort(404)
