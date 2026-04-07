from flask import Blueprint, render_template, session
from auth.decorators import login_required, role_required
from database.models import Person, ResearchProject, ProjectPerson, Publication, IPR, Startup
from database.db import db

student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('/dashboard')
@login_required
@role_required('Student')
def dashboard():
    student_id = session['user_id']

    project_links = db.session.query(ResearchProject).join(
        ProjectPerson, ProjectPerson.project_id == ResearchProject.project_id
    ).filter(
        ProjectPerson.person_id == student_id
    ).all()

    return render_template('student/dashboard.html', projects=project_links)


@student_bp.route('/projects')
@login_required
@role_required('Student')
def projects():
    student_id = session['user_id']

    projects = db.session.query(ResearchProject).join(
        ProjectPerson, ProjectPerson.project_id == ResearchProject.project_id
    ).filter(
        ProjectPerson.person_id == student_id
    ).all()

    return render_template('student/projects_list.html', projects=projects)


@student_bp.route('/project/<int:project_id>')
@login_required
@role_required('Student')
def view_project(project_id):
    student_id = session['user_id']
    project = ResearchProject.query.get(project_id)

    if not project:
        return "Project not found", 404

    membership = ProjectPerson.query.filter_by(
        project_id=project_id,
        person_id=student_id
    ).first()

    if not membership:
        return "Unauthorized or Project not found", 404

    publications = Publication.query.filter_by(project_id=project_id).all()
    iprs = IPR.query.join(Publication, IPR.publication_id == Publication.publication_id).filter(
        Publication.project_id == project_id
    ).all()
    startup = Startup.query.filter_by(project_id=project_id).first()

    return render_template('student/project_details.html', project=project, publications=publications, iprs=iprs, startup=startup)
