from flask import Blueprint, request, jsonify

from app.controllers.auth_controller import (
    register_user,
    authenticate_user,
    generate_token,
    AuthError,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    try:
        user = register_user(data.get("username"), data.get("password"))
        token = generate_token(user)
        return jsonify(token=token, user=user.to_dict()), 201
    except AuthError as e:
        return jsonify(error=e.message), e.status_code


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    try:
        user = authenticate_user(data.get("username"), data.get("password"))
        token = generate_token(user)
        return jsonify(token=token, user=user.to_dict()), 200
    except AuthError as e:
        return jsonify(error=e.message), e.status_code
