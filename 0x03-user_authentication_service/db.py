#!/usr/bin/env python3
""" Flask app
"""
from auth import Auth
from flask import Flask, abort, jsonify, request, redirect
from db import DB

app = Flask(__name__)
AUTH = Auth()
DB_INSTANCE = DB()


@app.route("/", methods=['GET'], strict_slashes=False)
def index() -> str:
    """ Return JSON response: {"message": "Bienvenue"} """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=['POST'], strict_slashes=False)
def users() -> str:
    """ Register new users """
    email = request.form.get("email")
    password = request.form.get("password")
    try:
        # Use DB to add user
        hashed_password = AUTH.hash_password(password)
        user = DB_INSTANCE.add_user(email, hashed_password)
    except ValueError:
        return jsonify(
            {"message": "email already registered"}
        ), 400
    return jsonify({"email": email, "message": "user created"}), 201


@app.route("/sessions", methods=["POST"], strict_slashes=False)
def login() -> str:
    """ Log in a user if credentials are correct """
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if user exists in DB
    try:
        user = DB_INSTANCE.find_user_by(email=email)
    except NoResultFound:
        abort(401)

    if not AUTH.valid_login(email, password):
        abort(401)

    session_id = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie("session_id", session_id)
    return response


@app.route("/sessions", methods=['DELETE'], strict_slashes=False)
def logout():
    """ Log out a user and destroy their session """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user is None or session_id is None:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect("/")


@app.route("/profile", methods=['GET'], strict_slashes=False)
def profile() -> str:
    """ Return user's email based on session_id """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": user.email}), 200
    abort(403)


@app.route("/reset_password", methods=['POST'], strict_slashes=False)
def get_reset_password_token() -> str:
    """ Generate a token for resetting user's password """
    email = request.form.get("email")
    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)
    return jsonify({"email": email, "reset_token": reset_token})


@app.route("/update_password", methods=['POST'], strict_slashes=False)
def update_password() -> str:
    """ Update user's password """
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")
    try:
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)
    return jsonify(
        {"email": email, "message": "password updated"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
