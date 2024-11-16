#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import CORS
import os

app = Flask(__name__)

# Register blueprint for views
app.register_blueprint(app_views, url_prefix="/api/v1")
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialize authentication based on AUTH_TYPE
auth = None
AUTH_TYPE = os.getenv("AUTH_TYPE")
if AUTH_TYPE == "auth":
    from api.v1.auth.auth import Auth
    auth = Auth()
elif AUTH_TYPE == "basic_auth":
    from api.v1.auth.basic_auth import BasicAuth
    auth = BasicAuth()
elif AUTH_TYPE == "session_auth":
    from api.v1.auth.session_auth import SessionAuth
    auth = SessionAuth()
elif AUTH_TYPE == "session_exp_auth":
    from api.v1.auth.session_exp_auth import SessionExpAuth
    auth = SessionExpAuth()
elif AUTH_TYPE == "session_db_auth":
    from api.v1.auth.session_db_auth import SessionDBAuth
    auth = SessionDBAuth()


@app.before_request
def bef_req():
    """
    Filtering each request
    """
    allowed_paths = [
        '/api/v1/status/',
        '/api/v1/unauthorized/',
        '/api/v1/forbidden/',
        '/api/v1/auth_session/login/'
    ]

    if auth is None:
        return

    # Check if the request path is excluded from authentication
    if not auth.require_auth(request.path, allowed_paths):
        return

    # Check for either an Authorization header or a session cookie
    if not auth.authorization_header(request) and \
            not auth.session_cookie(request):
        return abort(401, description="Unauthorized")

    # Check for a valid user
    if auth.current_user(request) is None:
        return abort(403, description="Forbidden")

    # Attach the current user to the request object
    request.current_user = auth.current_user(request)


@app.errorhandler(404)
def not_found(error) -> str:
    """ Not found handler """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> str:
    """ Unauthorized request handler """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """ Forbidden request handler """
    return jsonify({"error": "Forbidden"}), 403


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
