import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    instance_dir = os.path.join(os.path.dirname(app.root_path), "instance")
    os.makedirs(instance_dir, exist_ok=True)

    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)

    from app.views.auth_views import auth_bp
    from app.views.task_views import task_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(task_bp, url_prefix="/api/tasks")

    @app.route("/api/health")
    def health():
        return jsonify(status="ok"), 200

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify(error="Not found"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify(error="Internal server error"), 500

    with app.app_context():
        from app.models import user, task  # noqa: F401
        db.create_all()

    return app
