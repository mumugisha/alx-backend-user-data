#!/usr/bin/env python3
"""
Main file for testing the Flask app.
"""

import pytest
from app import app, AUTH


@pytest.fixture
def client():
    """Provide a test client for the Flask app."""
    app.testing = True
    return app.test_client()


def test_logout_success(client, mocker):
    """Test successful logout."""
    # Mock session ID and user retrieval
    mocker.patch.object(
        AUTH, 'get_user_from_session_id', return_value=mocker.Mock(id=1)
    )
    mocker.patch.object(AUTH, 'destroy_session', return_value=None)

    # Simulate request with a valid session_id
    response = client.delete(
        "/sessions", cookies={"session_id": "valid_session_id"}
    )

    # Assert redirection after logout
    assert response.status_code == 302
    assert response.location == "http://localhost/"


def test_logout_invalid_session(client, mocker):
    """Test logout with an invalid session."""
    # Mock invalid session ID
    mocker.patch.object(AUTH, 'get_user_from_session_id', return_value=None)

    # Simulate request with
