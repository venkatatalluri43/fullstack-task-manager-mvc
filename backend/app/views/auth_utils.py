from functools import wraps

from flask import request, jsonify

from app.controllers.auth_controller import decode_token, AuthError


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify(error="Missing or invalid Authorization header"), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except AuthError as e:
            return jsonify(error=e.message), e.status_code

        request.user_id = payload["sub"]
        request.username = payload["username"]
        return f(*args, **kwargs)

    return decorated
