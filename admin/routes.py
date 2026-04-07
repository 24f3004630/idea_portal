from flask import Blueprint, render_template, request, redirect
from database.models import Person, ResearchProject
from database.db import db
from auth.decorators import login_required, role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ---------------- DASHBOARD ----------------
@admin_bp.route('/dashboard')
@login_required
@role_required('Admin')
def dashboard():
    total_users = Person.query.count()
    total_students = Person.query.filter_by(type='Student').count()
    total_faculty = Person.query.filter_by(type='Faculty').count()
    total_projects = ResearchProject.query.count()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_students=total_students,
                           total_faculty=total_faculty,
                           total_projects=total_projects)


# ---------------- VIEW USERS ----------------
@admin_bp.route('/users')
@login_required
@role_required('Admin')
def view_users():
    users = Person.query.all()
    return render_template('admin/users.html', users=users)


# ---------------- APPROVE FACULTY ----------------
@admin_bp.route('/approve/<int:user_id>')
@login_required
@role_required('Admin')
def approve_user(user_id):
    user = Person.query.get(user_id)
    if user:
        user.is_approved = True
        db.session.commit()
    return redirect('/admin/users')


# ---------------- REJECT / DELETE USER ----------------
@admin_bp.route('/delete/<int:user_id>')
@login_required
@role_required('Admin')
def delete_user(user_id):
    user = Person.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect('/admin/users')


# ---------------- SEARCH USERS ----------------
@admin_bp.route('/search', methods=['GET'])
@login_required
@role_required('Admin')
def search_users():
    query = request.args.get('q')
    users = Person.query.filter(Person.name.contains(query)).all()
    return render_template('admin/users.html', users=users)


# ---------------- VIEW PROJECTS ----------------
@admin_bp.route('/projects')
@login_required
@role_required('Admin')
def view_projects():
    projects = ResearchProject.query.all()
    return render_template('admin/projects.html', projects=projects)


# ---------------- APPROVE PROJECT ----------------
@admin_bp.route('/approve_project/<int:project_id>')
@login_required
@role_required('Admin')
def approve_project(project_id):
    project = ResearchProject.query.get(project_id)
    if project:
        project.is_approved = True
        db.session.commit()
    return redirect('/admin/projects')