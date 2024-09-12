#!/usr/bin/env python3

"""Integration testing."""
import uuid

import requests

API_URL = "http://localhost:5000"


def register_user(email: str, password: str) -> None:
    """Test the User registration endpoint."""
    response = requests.post(
        url=f"{API_URL}/users",
        data={"email": email, "password": password},
    )

    assert response.status_code == 200
    assert response.json() == {
        "email": email,
        "message": "user created",
    }


def log_in_wrong_password(email: str, password: str) -> None:
    """Test the login endpoint with invalid credentials."""
    response = requests.post(
        url=f"{API_URL}/sessions", data={"email": email, "password": password}
    )

    assert response.status_code == 401

    # if log in didn't work, the session cookie should not be set.
    assert response.cookies.get("session_id") is None


def log_in(email: str, password: str) -> str:
    """Test the login endpoint with valid credentials."""
    response = requests.post(
        url=f"{API_URL}/sessions", data={"email": email, "password": password}
    )

    assert response.status_code == 200
    assert response.cookies.get("session_id") is not None

    assert response.json() == {"email": email, "message": "logged in"}

    # use the token for something real quick
    session_id = response.cookies.get("session_id")
    profile_response = requests.get(
        url=f"{API_URL}/profile",
        cookies={"session_id": session_id},
    )

    assert profile_response.status_code == 200
    data = profile_response.json()

    assert data.get("email") == email
    return session_id


def profile_unlogged() -> None:
    """Test the /profile endpoint without authentication."""
    response = requests.get(url=f"{API_URL}/profile")

    assert response.status_code == 403


def profile_logged(session_id: str) -> None:
    """Test the /profile endpoint with authenticated user."""
    response = requests.get(
        url=f"{API_URL}/profile", cookies={"session_id": session_id}
    )

    assert response.status_code == 200
    assert response.json() == {"email": EMAIL}


def log_out(session_id: str) -> None:
    """Test the logout endpoint."""
    response = requests.delete(
        url=f"{API_URL}/sessions",
        cookies={"session_id": session_id},
        allow_redirects=False,
    )

    # verify that redirection worked
    assert response.status_code == 302
    next_url = response.headers.get("Location")

    assert next_url == "/"

    # now let's manually follow through to end of the redirection.
    next_response = requests.get(url=f"{API_URL}{next_url}")
    assert next_response.status_code == 200


def reset_password_token(email: str) -> str:
    """Test password reset token endpoint."""
    response = requests.post(
        url=f"{API_URL}/reset_password", data={"email": email}
    )

    assert response.status_code == 200
    data = response.json()

    assert data.get("email") == email

    token = data.get("reset_token")
    assert token is not None

    # try converting token to a UUID, a valid token won't break the code
    uuid_token = uuid.UUID(token)

    assert token == str(uuid_token)
    return token


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """Test the password update endpoint."""
    response = requests.put(
        url=f"{API_URL}/reset_password",
        data={
            "email": email,
            "reset_token": reset_token,
            "new_password": new_password,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "Password updated"}


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"

if __name__ == "__main__":

    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
