from flask import Blueprint, request, jsonify

from app.controllers.project_controller import (
    list_projects,
    create_project,
    update_project,
    delete_project,
    get_project,
    ProjectError,
)
from app.views.auth_utils import login_required

project_bp = Blueprint("projects", __name__)


@project_bp.route("", methods=["GET"])
@login_required
def get_projects():
    projects = list_projects(request.user_id)
    return jsonify(projects=[p.to_dict() for p in projects]), 200


@project_bp.route("/<int:project_id>", methods=["GET"])
@login_required
def get_single_project(project_id):
    try:
        project = get_project(project_id)
        if project.owner_id != request.user_id:
            return jsonify(error="Not authorized to view this project"), 403
        return jsonify(project=project.to_dict()), 200
    except ProjectError as e:
        return jsonify(error=e.message), e.status_code


@project_bp.route("", methods=["POST"])
@login_required
def post_project():
    data = request.get_json(silent=True) or {}
    try:
        project = create_project(
            name=data.get("name"),
            description=data.get("description"),
            owner_id=request.user_id,
        )
        return jsonify(project=project.to_dict()), 201
    except ProjectError as e:
        return jsonify(error=e.message), e.status_code


@project_bp.route("/<int:project_id>", methods=["PUT", "PATCH"])
@login_required
def put_project(project_id):
    data = request.get_json(silent=True) or {}
    try:
        project = update_project(project_id, request.user_id, **data)
        return jsonify(project=project.to_dict()), 200
    except ProjectError as e:
        return jsonify(error=e.message), e.status_code


@project_bp.route("/<int:project_id>", methods=["DELETE"])
@login_required
def remove_project(project_id):
    try:
        delete_project(project_id, request.user_id)
        return "", 204
    except ProjectError as e:
        return jsonify(error=e.message), e.status_code
