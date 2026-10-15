from app import db
from app.models.task import Task

VALID_STATUSES = {"pending", "in_progress", "done"}


class TaskError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def list_tasks(user_id=None):
    query = Task.query
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    return query.order_by(Task.created_at.desc()).all()


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise TaskError("Task not found", 404)
    return task


def create_task(title, description, user_id, status="pending"):
    if not title or not title.strip():
        raise TaskError("Title is required", 400)
    if status not in VALID_STATUSES:
        raise TaskError(f"Status must be one of {sorted(VALID_STATUSES)}", 400)

    task = Task(title=title.strip(), description=description, status=status, user_id=user_id)
    db.session.add(task)
    db.session.commit()
    return task


def update_task(task_id, user_id, **fields):
    task = get_task(task_id)
    if task.user_id != user_id:
        raise TaskError("Not authorized to modify this task", 403)

    if "title" in fields and fields["title"] is not None:
        if not fields["title"].strip():
            raise TaskError("Title cannot be empty", 400)
        task.title = fields["title"].strip()
    if "description" in fields:
        task.description = fields["description"]
    if "status" in fields and fields["status"] is not None:
        if fields["status"] not in VALID_STATUSES:
            raise TaskError(f"Status must be one of {sorted(VALID_STATUSES)}", 400)
        task.status = fields["status"]

    db.session.commit()
    return task


def delete_task(task_id, user_id):
    task = get_task(task_id)
    if task.user_id != user_id:
        raise TaskError("Not authorized to delete this task", 403)
    db.session.delete(task)
    db.session.commit()
