from datetime import datetime, timezone

from app import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    tasks = db.relationship(
        "Task", foreign_keys="Task.user_id", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    projects = db.relationship(
        "Project", foreign_keys="Project.owner_id", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    assigned_tasks = db.relationship(
        "Task", foreign_keys="Task.assignee_id", backref="assignee", lazy=True
    )

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
        }
