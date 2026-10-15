import jwt
from datetime import datetime, timezone
from flask import current_app

from app import db
from app.models.user import User


class AuthError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_user(username, password):
    if not username or not password:
        raise AuthError("Username and password are required", 400)

    if User.query.filter_by(username=username).first():
        raise AuthError("Username already taken", 409)

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        raise AuthError("Invalid username or password", 401)
    return user


def generate_token(user):
    payload = {
        "sub": user.id,
        "username": user.username,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + current_app.config["JWT_EXPIRATION"],
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired", 401)
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token", 401)
