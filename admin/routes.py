from flask import Blueprint, render_template, request, redirect
from database.models import Person, ResearchProject, Publication, IPR, Startup
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
    active_users = Person.query.filter_by(is_approved=True).count()
    total_projects = ResearchProject.query.count()
    total_publications = Publication.query.count()
    total_iprs = IPR.query.count()
    total_startups = Startup.query.count()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_students=total_students,
                           total_faculty=total_faculty,
                           active_users=active_users,
                           total_projects=total_projects,
                           total_publications=total_publications,
                           total_iprs=total_iprs,
                           total_startups=total_startups)


# ---------------- VIEW USERS ----------------
@admin_bp.route('/users')
@login_required
@role_required('Admin')
def view_users():
    users = Person.query.all()
    return render_template('admin/users.html', users=users)


# ---------------- VIEW PENDING FACULTY ----------------
@admin_bp.route('/pending_faculty')
@login_required
@role_required('Admin')
def view_pending_faculty():
    pending_faculty = Person.query.filter_by(type='Faculty', is_approved=False).all()
    return render_template('admin/pending_faculty.html', users=pending_faculty)


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


# ---------------- REJECT USER ----------------
@admin_bp.route('/reject/<int:user_id>')
@login_required
@role_required('Admin')
def reject_user(user_id):
    user = Person.query.get(user_id)
    if user:
        user.is_approved = False
        db.session.commit()
    return redirect('/admin/users')


# ---------------- DEACTIVATE USER ----------------
@admin_bp.route('/deactivate/<int:user_id>')
@login_required
@role_required('Admin')
def deactivate_user(user_id):
    user = Person.query.get(user_id)
    if user:
        user.is_approved = False
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
        if project.project_status == 'Proposed':
            project.project_status = 'Ongoing'
        db.session.commit()
    return redirect('/admin/projects')


# ==================== VIEW PROJECTS BY STATUS ====================
@admin_bp.route('/projects/status/<status>')
@login_required
@role_required('Admin')
def projects_by_status(status):
    """View projects filtered by status"""
    valid_statuses = ['Proposed', 'Ongoing', 'Completed', 'On Hold']
    
    if status not in valid_statuses:
        return "Invalid status", 400
    
    projects = ResearchProject.query.filter_by(project_status=status).all()
    
    for project in projects:
        project.faculty = Person.query.get(project.faculty_id)
    
    return render_template('admin/projects_by_status.html',
                         projects=projects,
                         status=status)


# ==================== PROJECT LIFECYCLE VIEW ====================
@admin_bp.route('/project/<int:project_id>/lifecycle')
@login_required
@role_required('Admin')
def project_lifecycle(project_id):
    """View full project lifecycle: Project → Publication → IPR → Startup"""
    from database.models import Startup
    
    project = ResearchProject.query.get(project_id)
    
    if not project:
        return "Project not found", 404
    
    faculty = Person.query.get(project.faculty_id)
    team_members = db.session.query(ProjectPerson, Person).filter(
        ProjectPerson.project_id == project_id,
        ProjectPerson.person_id == Person.person_id
    ).all()
    
    # Get all output artifacts
    publications = Publication.query.filter_by(project_id=project_id).all()
    iprs = IPR.query.filter_by(project_id=project_id).all()
    startup = Startup.query.filter_by(project_id=project_id).first()
    
    return render_template('admin/project_lifecycle.html',
                         project=project,
                         faculty=faculty,
                         team_members=team_members,
                         publications=publications,
                         iprs=iprs,
                         startup=startup)


# ==================== PUBLICATION MONITORING ====================
@admin_bp.route('/publications')
@login_required
@role_required('Admin')
def view_publications():
    """View all publications with their statuses"""
    publications = Publication.query.all()
    
    pub_data = []
    for pub in publications:
        project = ResearchProject.query.get(pub.project_id)
        pub_data.append({
            'publication': pub,
            'project': project,
            'faculty': Person.query.get(project.faculty_id) if project else None
        })
    
    return render_template('admin/publications.html', pub_data=pub_data)


# ==================== IPR/PATENT MONITORING ====================
@admin_bp.route('/iprs')
@login_required
@role_required('Admin')
def view_iprs():
    """View all IPRs/Patents with their grant statuses"""
    iprs = IPR.query.all()
    
    ipr_data = []
    for ipr in iprs:
        project = ResearchProject.query.get(ipr.project_id)
        ipr_data.append({
            'ipr': ipr,
            'project': project,
            'faculty': Person.query.get(project.faculty_id) if project else None
        })
    
    return render_template('admin/iprs.html', ipr_data=ipr_data)


# ==================== STARTUP TRACKING ====================
@admin_bp.route('/startups')
@login_required
@role_required('Admin')
def view_startups():
    """View all startups converted from projects"""
    startups = Startup.query.all()
    
    startup_data = []
    for startup in startups:
        project = ResearchProject.query.get(startup.project_id)
        startup_data.append({
            'startup': startup,
            'project': project,
            'faculty': Person.query.get(project.faculty_id) if project else None
        })
    
    return render_template('admin/startups.html', startup_data=startup_data)
    return redirect('/admin/projects')