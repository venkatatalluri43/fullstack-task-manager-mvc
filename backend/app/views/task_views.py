from flask import Blueprint, request, jsonify

from app.controllers.task_controller import (
    list_tasks,
    create_task,
    update_task,
    delete_task,
    get_task,
    TaskError,
)
from app.views.auth_utils import login_required

task_bp = Blueprint("tasks", __name__)


@task_bp.route("", methods=["GET"])
@login_required
def get_tasks():
    scope = request.args.get("scope", "mine")
    project_id = request.args.get("project_id", type=int)
    assigned_to_me = request.args.get("assigned_to_me")

    user_id = request.user_id if scope == "mine" else None
    assignee_id = request.user_id if assigned_to_me == "true" else None

    tasks = list_tasks(user_id=user_id, project_id=project_id, assignee_id=assignee_id)
    return jsonify(tasks=[t.to_dict() for t in tasks]), 200


@task_bp.route("/<int:task_id>", methods=["GET"])
@login_required
def get_single_task(task_id):
    try:
        task = get_task(task_id)
        return jsonify(task=task.to_dict()), 200
    except TaskError as e:
        return jsonify(error=e.message), e.status_code


@task_bp.route("", methods=["POST"])
@login_required
def post_task():
    data = request.get_json(silent=True) or {}
    try:
        task = create_task(
            title=data.get("title"),
            description=data.get("description"),
            user_id=request.user_id,
            project_id=data.get("project_id"),
            status=data.get("status", "pending"),
            priority=data.get("priority", "medium"),
            due_date=data.get("due_date"),
            assignee_id=data.get("assignee_id"),
        )
        return jsonify(task=task.to_dict()), 201
    except TaskError as e:
        return jsonify(error=e.message), e.status_code


@task_bp.route("/<int:task_id>", methods=["PUT", "PATCH"])
@login_required
def put_task(task_id):
    data = request.get_json(silent=True) or {}
    try:
        task = update_task(task_id, request.user_id, **data)
        return jsonify(task=task.to_dict()), 200
    except TaskError as e:
        return jsonify(error=e.message), e.status_code


@task_bp.route("/<int:task_id>", methods=["DELETE"])
@login_required
def remove_task(task_id):
    try:
        delete_task(task_id, request.user_id)
        return "", 204
    except TaskError as e:
        return jsonify(error=e.message), e.status_code
