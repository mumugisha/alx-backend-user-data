#!/usr/bin/env python3
"""
This module initializes the app views for the API.
It sets up the URL prefix for version 1 of the API and imports
the necessary routes for index, users, and session authentication.
"""

# Importing required modules and functions at the top
from flask import Blueprint
from api.v1.views.index import index_view
from api.v1.views.users import users_view
from api.v1.views.session_auth import session_auth_view
from api.v1.models.user import User

# Creating a Blueprint instance for app views
app_views = Blueprint("app_views", __name__, url_prefix="/api/v1")

# Register the views with the blueprint (to be added at the end of the file)
app_views.add_url_rule("/", view_func=index_view)
app_views.add_url_rule("/users", view_func=users_view)
app_views.add_url_rule("/session", view_func=session_auth_view)

# Load user data from a file, if required by the app
User.load_from_file()
