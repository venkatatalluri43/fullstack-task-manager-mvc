from app import db
from app.models.project import Project


class ProjectError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def list_projects(user_id):
    return Project.query.filter_by(owner_id=user_id).order_by(Project.created_at.desc()).all()


def get_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        raise ProjectError("Project not found", 404)
    return project


def create_project(name, description, owner_id):
    if not name or not name.strip():
        raise ProjectError("Project name is required", 400)

    project = Project(name=name.strip(), description=description, owner_id=owner_id)
    db.session.add(project)
    db.session.commit()
    return project


def update_project(project_id, user_id, **fields):
    project = get_project(project_id)
    if project.owner_id != user_id:
        raise ProjectError("Not authorized to modify this project", 403)

    if "name" in fields and fields["name"] is not None:
        if not fields["name"].strip():
            raise ProjectError("Project name cannot be empty", 400)
        project.name = fields["name"].strip()
    if "description" in fields:
        project.description = fields["description"]

    db.session.commit()
    return project


def delete_project(project_id, user_id):
    project = get_project(project_id)
    if project.owner_id != user_id:
        raise ProjectError("Not authorized to delete this project", 403)
    db.session.delete(project)
    db.session.commit()
