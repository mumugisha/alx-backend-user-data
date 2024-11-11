#!/usr/bin/env python3
""" Module of Index views
"""
from flask import jsonify, abort
from api.v1.views import app_views


@app_views.route('/unauthorized', methods=['GET'], strict_slashes=False)
def unauthorized() -> str:
    """ GET /api/v1/unauthorized
    Raises:
      - 401 error with a description
    """
    abort(401, description="unauthorized")


@app_views.route('/forbidden', methods=['GET'], strict_slashes=False)
def forbidden() -> str:
    """ GET /api/v1/forbidden
    Raises:
      - 403 error with a description
    """
    abort(403, description="forbidden")


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status() -> str:
    """ GET /api/v1/status
    Returns:
      - JSON response with the status of the API
    """
    return jsonify({"status": "OK"})


@app_views.route('/stats/', strict_slashes=False)
def stats() -> str:
    """ GET /api/v1/stats
    Returns:
      - JSON response with the count of each object type
    """
    from models.user import User
    stats = {}
    stats['users'] = User.count()  # Add additional counts if needed
    return jsonify(stats)
