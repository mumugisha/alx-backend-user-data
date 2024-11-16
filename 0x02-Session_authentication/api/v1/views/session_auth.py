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


@app_views.route('/auth_session/logout', methods=['DELETE'], strict_slashes=False)
def handle_logout():
    """
    Function to handle logout
    """
    from api.v1.app import auth
    if auth.destroy_session(request):
        return jsonify({}), 200
    else:
        # Log or print details about the request and session
        print(f"Failed to destroy session for user: {request.cookies.get('_my_session_id')}")
        abort(404)
