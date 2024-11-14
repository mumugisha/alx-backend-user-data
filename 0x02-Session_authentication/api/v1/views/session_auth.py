#!/usr/bin/env python3
"""
Handles all routes for Session authentication
"""

import os
from flask import jsonify, request
from api.v1.views import app_views
from models.user import User


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def auth_session_login():
    """
    Handles the user login via Session Authentication.
    Returns:
        JSON dictionary representation of the User if login is successful.
        Returns an error JSON response otherwise.
    """
    email = request.form.get('email')
    password = request.form.get('password')

    # Check for missing email
    if email is None or email == '':
        return jsonify({"error": "email missing"}), 400

    # Check for missing password
    if password is None or password == '':
        return jsonify({"error": "password missing"}), 400

    # Find user by email
    users = User.search({"email": email})
    if not users or len(users) == 0:
        return jsonify({"error": "no user found for this email"}), 404

    # Validate password
    for user in users:
        if user.is_valid_password(password):
            # Import auth here to avoid circular dependency
            from api.v1.app import auth
            session_id = auth.create_session(user.id)
            
            # Create response with user data
            response = jsonify(user.to_json())
            
            # Set session cookie
            session_name = os.getenv('SESSION_NAME', 'SESSION_ID')
            response.set_cookie(session_name, session_id)
            return response

    # Incorrect password
    return jsonify({"error": "wrong password"}), 401
