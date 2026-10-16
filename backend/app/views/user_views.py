from flask import Blueprint, jsonify

from app.models.user import User
from app.views.auth_utils import login_required

user_bp = Blueprint("users", __name__)


@user_bp.route("", methods=["GET"])
@login_required
def get_users():
    users = User.query.order_by(User.username).all()
    return jsonify(users=[u.to_dict() for u in users]), 200
