#!/usr/bin/env python3

"""App module."""

import os
from typing import Tuple

from flask import Flask, abort, jsonify, redirect, request
from werkzeug import Response

import utils
from auth import Auth

AUTH = Auth()
app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route("/", methods=["GET"])
def root():
    """API Root."""
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"])
def users() -> Tuple[Response, int]:
    """Register new user."""
    success, err_msg = utils.request_body_provided(
        expected_fields={"email", "password"}
    )
    if not success:
        return jsonify({"message": err_msg}), 400

    email = request.form.get("email")
    password = request.form.get("password")

    try:
        AUTH.register_user(email=email, password=password)
    except ValueError as err:
        err_msg = str(err)
        if "already exists" in err_msg:
            return jsonify({"message": "email already registered"}), 400
        return jsonify({"message": err_msg}), 400

    return jsonify({"email": email, "message": "user created"}), 200


@app.route("/sessions", methods=["POST"])
def login() -> Tuple[Response, int]:
    """User login endpoint.

    This endpoint accepts and logs user into the system if the credentials
    provided are valid. In the event of invalid data, the user receives an
    authorization error with the code 401.

    Upon successful login, a session is created for the authenticated user.
    """
    success, err_msg = utils.request_body_provided(
        expected_fields={"email", "password"}
    )
    if not success:
        return jsonify({"message": err_msg}), 400

    email = request.form.get("email")
    password = request.form.get("password")

    if not AUTH.valid_login(email=email, password=password):
        abort(401)

    session_id = AUTH.create_session(email=email)
    data = jsonify({"email": email, "message": "logged in"})
    data.set_cookie(key="session_id", value=session_id)

    return data, 200


@app.route("/sessions", methods=["DELETE"])
def logout() -> Response:
    """Log user out of the session."""
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id=session_id)
    if not user:
        abort(403)

    AUTH.destroy_session(user_id=user.id)
    return redirect(location="/")


@app.route("/profile", methods=["GET"])
def profile() -> Response:
    """Get the current authenticated user's profile."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        abort(403)

    db_user = AUTH.get_user_from_session_id(session_id=session_id)
    if not db_user:
        abort(403)

    return jsonify({"email": db_user.email})


@app.route("/reset_password", methods=["POST"])
def get_reset_password_token() -> Tuple[Response, int]:
    """Get the token for user password reset."""
    success, err_msg = utils.request_body_provided(expected_fields={"email"})
    if not success:
        return jsonify({"message": err_msg}), 400

    email = request.form.get("email")

    try:
        reset_token = AUTH.get_reset_password_token(email=email)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "reset_token": reset_token}), 200


@app.route("/reset_password", methods=["PUT"])
def update_password() -> Tuple[Response, int]:
    """Update the user's password."""
    success, err_msg = utils.request_body_provided(
        expected_fields={"email", "reset_token", "new_password"}
    )
    if not success:
        return jsonify({"message": err_msg}), 400

    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")

    try:
        AUTH.update_password(reset_token=reset_token, password=new_password)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "message": "Password updated"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("DEBUG") == "True")
