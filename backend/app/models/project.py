from datetime import datetime, timezone

from app import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    tasks = db.relationship(
        "Task", foreign_keys="Task.project_id", backref="project", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        done = sum(1 for t in self.tasks if t.status == "done")
        total = len(self.tasks)
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "owner": self.owner.username if self.owner else None,
            "created_at": self.created_at.isoformat(),
            "task_count": total,
            "done_count": done,
        }
