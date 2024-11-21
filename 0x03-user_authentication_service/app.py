#!/usr/bin/env python3
""" Flask app
"""
from flask import (
    Flask, abort, jsonify, request, redirect
)
from typing import Optional, Tuple
from auth import Auth

AUTH = Auth()
app = Flask(__name__)


@app.route("/", methods=['GET'], strict_slashes=False)
def index() -> str:
    """ Return JSON response: {"message": "Bienvenue"} """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=['POST'], strict_slashes=False)
def users() -> str:
    """
    Register new users via POST request.
    Expects email and password.

    Returns:
        JSON response with status.
    """
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    if not email or not password:
        abort(400)
    try:
        AUTH.register_user(email, password)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"], strict_slashes=False)
def login() -> Optional[Tuple]:
    """ Validate a user if credentials are correct """
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    if not email or not password:
        abort(401)

    if not AUTH.valid_login(email, password):
        abort(401)

    session_id = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie("session_id", session_id)
    return response


@app.route("/sessions", methods=['DELETE'], strict_slashes=False)
def logout() -> str:
    """ Log out a user and destroy their session """
    session_id = request.cookies.get("session_id")
    if not session_id:
        abort(403)

    user = AUTH.get_user_from_session_id(session_id)
    if not user:
        abort(403)

    AUTH.destroy_session(user.id)
    return redirect("/")


@app.route("/profile", methods=['GET'], strict_slashes=False)
def profile() -> str:
    """ Return user's email based on session_id """
    session_id = request.cookies.get("session_id")
    if not session_id:
        abort(403)

    user = AUTH.get_user_from_session_id(session_id)
    if not user:
        abort(403)

    return jsonify({"email": user.email})


@app.route("/reset_password", methods=['POST'], strict_slashes=False)
def get_reset_password_token() -> str:
    """ Generate a token for resetting user's password """
    email = request.form.get("email", "").strip()
    if not email:
        abort(403)

    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": reset_token})
    except Exception:
        abort(403)


@app.route("/update_password", methods=['PUT'], strict_slashes=False)
def update_password() -> str:
    """ Update user's password """
    email = request.form.get("email", "").strip()
    reset_token = request.form.get("reset_token", "").strip()
    new_password = request.form.get("new_password", "").strip()
    if not email or not reset_token or not new_password:
        abort(403)

    try:
        AUTH.update_password(reset_token, new_password)
        return jsonify({"email": email, "message": "password updated"})
    except Exception:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
