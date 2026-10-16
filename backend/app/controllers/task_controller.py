from datetime import datetime

from app import db
from app.models.task import Task
from app.models.project import Project
from app.models.user import User

VALID_STATUSES = {"pending", "in_progress", "done"}
VALID_PRIORITIES = {"low", "medium", "high"}


class TaskError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _parse_due_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise TaskError("due_date must be in YYYY-MM-DD format", 400)


def list_tasks(user_id=None, project_id=None, assignee_id=None):
    query = Task.query
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    if project_id is not None:
        query = query.filter_by(project_id=project_id)
    if assignee_id is not None:
        query = query.filter_by(assignee_id=assignee_id)
    return query.order_by(Task.due_date.is_(None), Task.due_date.asc(), Task.created_at.desc()).all()


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise TaskError("Task not found", 404)
    return task


def create_task(
    title, description, user_id, project_id, status="pending",
    priority="medium", due_date=None, assignee_id=None,
):
    if not title or not title.strip():
        raise TaskError("Title is required", 400)
    if status not in VALID_STATUSES:
        raise TaskError(f"Status must be one of {sorted(VALID_STATUSES)}", 400)
    if priority not in VALID_PRIORITIES:
        raise TaskError(f"Priority must be one of {sorted(VALID_PRIORITIES)}", 400)

    project = db.session.get(Project, project_id) if project_id else None
    if not project:
        raise TaskError("Project not found", 404)
    if project.owner_id != user_id:
        raise TaskError("Not authorized to add tasks to this project", 403)

    assignee_id = assignee_id or user_id
    if not db.session.get(User, assignee_id):
        raise TaskError("Assignee not found", 400)

    task = Task(
        title=title.strip(),
        description=description,
        status=status,
        priority=priority,
        due_date=_parse_due_date(due_date),
        user_id=user_id,
        project_id=project_id,
        assignee_id=assignee_id,
    )
    db.session.add(task)
    db.session.commit()
    return task


def update_task(task_id, user_id, **fields):
    task = get_task(task_id)
    is_owner = task.user_id == user_id
    is_assignee = task.assignee_id == user_id

    if not is_owner and not is_assignee:
        raise TaskError("Not authorized to modify this task", 403)

    if not is_owner:
        disallowed = set(fields) - {"status"}
        if disallowed:
            raise TaskError("Assignees may only update task status", 403)

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
    if "priority" in fields and fields["priority"] is not None:
        if fields["priority"] not in VALID_PRIORITIES:
            raise TaskError(f"Priority must be one of {sorted(VALID_PRIORITIES)}", 400)
        task.priority = fields["priority"]
    if "due_date" in fields:
        task.due_date = _parse_due_date(fields["due_date"])
    if "assignee_id" in fields and fields["assignee_id"] is not None:
        if not db.session.get(User, fields["assignee_id"]):
            raise TaskError("Assignee not found", 400)
        task.assignee_id = fields["assignee_id"]

    db.session.commit()
    return task


def delete_task(task_id, user_id):
    task = get_task(task_id)
    if task.user_id != user_id:
        raise TaskError("Not authorized to delete this task", 403)
    db.session.delete(task)
    db.session.commit()
