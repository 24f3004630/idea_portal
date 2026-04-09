from flask import Blueprint, render_template, request, redirect, session, jsonify
from database.db import db
from database.models import (
    Person, ResearchProject, ProjectPerson, Publication, IPR, Startup, 
    Competition, Funder, ProjectFunding, PublicationAuthor, Author
)
from auth.decorators import login_required, role_required, faculty_can_create_projects, approved_required
from datetime import datetime

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')


# ==================== DASHBOARD ====================
@faculty_bp.route('/dashboard')
@login_required
@role_required('Faculty')
def dashboard():
    """Faculty dashboard showing overview of projects and activities"""
    faculty_id = session['user_id']
    
    # Get faculty projects
    projects = ResearchProject.query.filter_by(faculty_id=faculty_id).all()
    
    # Calculate statistics
    total_projects = len(projects)
    ongoing_projects = len([p for p in projects if p.project_status == 'Ongoing'])
    completed_projects = len([p for p in projects if p.project_status == 'Completed'])
    startup_conversions = len([p for p in projects if p.is_startup_converted])
    
    # Get recent publications
    publications = Publication.query.join(
        ResearchProject, Publication.project_id == ResearchProject.project_id
    ).filter(
        ResearchProject.faculty_id == faculty_id
    ).order_by(Publication.publication_date.desc()).limit(5).all()
    
    # Get IPRs/Patents
    iprs = IPR.query.join(
        Publication, IPR.publication_id == Publication.publication_id
    ).join(
        ResearchProject, Publication.project_id == ResearchProject.project_id
    ).filter(
        ResearchProject.faculty_id == faculty_id
    ).all()
    
    return render_template('faculty/dashboard.html',
                         projects=projects,
                         total_projects=total_projects,
                         ongoing_projects=ongoing_projects,
                         completed_projects=completed_projects,
                         startup_conversions=startup_conversions,
                         publications=publications,
                         iprs=iprs)


# ==================== CREATE PROJECT ====================
@faculty_bp.route('/project/create', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
@faculty_can_create_projects
def create_project():
    """Create a new research project"""
    if request.method == 'POST':
        try:
            faculty_id = session['user_id']
            
            project = ResearchProject(
                faculty_id=faculty_id,
                project_title=request.form.get('project_title'),
                project_description=request.form.get('project_description'),
                domain=request.form.get('domain'),
                department=request.form.get('department'),
                required_skills=request.form.get('required_skills'),
                team_size=int(request.form.get('team_size', 1)),
                project_status='Proposed',
                program_location=request.form.get('program_location', '')
            )
            
            db.session.add(project)
            db.session.commit()
            
            # Add faculty as project lead
            project_person = ProjectPerson(
                project_id=project.project_id,
                person_id=faculty_id,
                role='Faculty Lead'
            )
            db.session.add(project_person)
            db.session.commit()
            
            return redirect(f'/faculty/project/{project.project_id}')
        except Exception as e:
            return f"Error creating project: {str(e)}"
    
    return render_template('faculty/create_project.html')


# ==================== VIEW PROJECT DETAILS ====================
@faculty_bp.route('/project/<int:project_id>')
@login_required
@role_required('Faculty')
def view_project(project_id):
    """View project details and manage it"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    # Get project team
    team_members = db.session.query(
        ProjectPerson, Person
    ).filter(
        ProjectPerson.project_id == project_id,
        ProjectPerson.person_id == Person.person_id
    ).all()
    
    # Get students in project
    students = Person.query.join(
        ProjectPerson, Person.person_id == ProjectPerson.person_id
    ).filter(
        ProjectPerson.project_id == project_id,
        Person.type == 'Student'
    ).all()
    
    # Get available students (approved students not in this project)
    used_student_ids = db.session.query(ProjectPerson.person_id).filter(
        ProjectPerson.project_id == project_id
    ).all()
    used_student_ids = [s[0] for s in used_student_ids]
    
    available_students = Person.query.filter(
        Person.type == 'Student',
        Person.is_approved == True,
        ~Person.person_id.in_(used_student_ids)
    ).all()
    
    # Get project publications
    publications = Publication.query.filter_by(project_id=project_id).all()
    
    # Get project funding
    fundings = db.session.query(
        ProjectFunding, Funder
    ).filter(
        ProjectFunding.project_id == project_id,
        ProjectFunding.fund_id == Funder.fund_id
    ).all()
    
    # Get project IPRs
    iprs = IPR.query.join(
        Publication, IPR.publication_id == Publication.publication_id
    ).filter(
        Publication.project_id == project_id
    ).all()
    
    return render_template('faculty/project_details.html',
                         project=project,
                         team_members=team_members,
                         students=students,
                         available_students=available_students,
                         publications=publications,
                         fundings=fundings,
                         iprs=iprs)


# ==================== UPDATE PROJECT STATUS ====================
@faculty_bp.route('/project/<int:project_id>/update-status', methods=['POST'])
@login_required
@role_required('Faculty')
def update_project_status(project_id):
    """Update project status (Ongoing / Completed / On Hold)"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    new_status = request.form.get('project_status')
    if new_status in ['Ongoing', 'Completed', 'On Hold']:
        project.project_status = new_status
        db.session.commit()
        return redirect(f'/faculty/project/{project_id}')
    
    return "Invalid status", 400


# ==================== ADD STUDENT TO PROJECT ====================
@faculty_bp.route('/project/<int:project_id>/add-student', methods=['POST'])
@login_required
@role_required('Faculty')
def add_student_to_project(project_id):
    """Add a student to the project team"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    try:
        student_id = request.form.get('student_id')
        role = request.form.get('role', 'Team Member')
        
        # Check if student already in project
        existing = ProjectPerson.query.filter_by(
            project_id=project_id,
            person_id=student_id
        ).first()
        
        if existing:
            return "Student already in this project", 400

        if not project.is_approved:
            return "Cannot add students to an unapproved project", 400
        
        # Verify student exists and is actually a student
        student = Person.query.get(student_id)
        if not student or student.type != 'Student':
            return "Invalid student", 400
        
        project_person = ProjectPerson(
            project_id=project_id,
            person_id=student_id,
            role=role
        )
        db.session.add(project_person)
        db.session.commit()
        
        return redirect(f'/faculty/project/{project_id}')
    except Exception as e:
        return f"Error adding student: {str(e)}", 400


# ==================== ASSIGN ROLE ====================
@faculty_bp.route('/project/<int:project_id>/assign-role/<int:person_id>', methods=['POST'])
@login_required
@role_required('Faculty')
def assign_role(project_id, person_id):
    """Update role for a team member"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    try:
        new_role = request.form.get('role')
        
        project_person = ProjectPerson.query.filter_by(
            project_id=project_id,
            person_id=person_id
        ).first()
        
        if not project_person:
            return "Team member not found", 404
        
        project_person.role = new_role
        db.session.commit()
        
        return redirect(f'/faculty/project/{project_id}')
    except Exception as e:
        return f"Error updating role: {str(e)}", 400


# ==================== REMOVE STUDENT FROM PROJECT ====================
@faculty_bp.route('/project/<int:project_id>/remove-student/<int:person_id>', methods=['POST'])
@login_required
@role_required('Faculty')
def remove_student_from_project(project_id, person_id):
    """Remove a student from the project"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    try:
        project_person = ProjectPerson.query.filter_by(
            project_id=project_id,
            person_id=person_id,
        ).first()
        
        if not project_person:
            return "Team member not found", 404
        
        db.session.delete(project_person)
        db.session.commit()
        
        return redirect(f'/faculty/project/{project_id}')
    except Exception as e:
        return f"Error removing student: {str(e)}", 400


# ==================== ADD PUBLICATION ====================
@faculty_bp.route('/project/<int:project_id>/publication/add', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def add_publication(project_id):
    """Add a publication to the project"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            doi = request.form.get('doi')

            query = Publication.query.filter(Publication.project_id == project_id)
            if doi:
                query = query.filter((Publication.title == title) | (Publication.doi == doi))
            else:
                query = query.filter(Publication.title == title)

            existing_publication = query.first()
            if existing_publication:
                return "Duplicate publication entry detected for this project", 400

            publication = Publication(
                project_id=project_id,
                title=title,
                publication_type=request.form.get('publication_type'),
                venue=request.form.get('venue'),
                status=request.form.get('status', 'Submitted'),
                indexing=request.form.get('indexing'),
                year_of_publication=int(request.form.get('year_of_publication', datetime.now().year)),
                volume=request.form.get('volume'),
                page_number=request.form.get('page_number'),
                doi=doi,
                issn_isbn=request.form.get('issn_isbn'),
                publisher=request.form.get('publisher')
            )
            
            db.session.add(publication)
            db.session.commit()
            
            return redirect(f'/faculty/project/{project_id}')
        except Exception as e:
            return f"Error adding publication: {str(e)}"
    
    return render_template('faculty/add_publication.html', project=project)


# ==================== ADD IPR / PATENT ====================
@faculty_bp.route('/project/<int:project_id>/ipr/add', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def add_ipr(project_id):
    """Add IPR/Patent to the project"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    if request.method == 'POST':
        try:
            publication_id = request.form.get('publication_id')
            innovation_title = request.form.get('innovation_title')
            application_number = request.form.get('application_number')

            if publication_id:
                publication = Publication.query.get(publication_id)
                if not publication or publication.project_id != project_id:
                    return "Invalid publication selected", 400
            else:
                publication = Publication(
                    project_id=project_id,
                    title=innovation_title,
                    publication_type='Patent',
                    status='Submitted'
                )
                db.session.add(publication)
                db.session.flush()
                publication_id = publication.publication_id

            if application_number:
                duplicate_ipr = IPR.query.filter_by(application_number=application_number).first()
                if duplicate_ipr:
                    return "Duplicate IPR entry detected by application number", 400

            duplicate_title = IPR.query.join(Publication).filter(
                Publication.project_id == project_id,
                IPR.innovation_title == innovation_title
            ).first()
            if duplicate_title:
                return "Duplicate IPR entry detected for this project", 400

            ipr = IPR(
                publication_id=publication_id,
                innovation_title=innovation_title,
                ipr_type=request.form.get('ipr_type'),
                application_number=application_number,
                grant_status=request.form.get('grant_status', 'Filed'),
                ownership_type=request.form.get('ownership_type', 'Individual')
            )
            
            db.session.add(ipr)
            db.session.commit()
            
            return redirect(f'/faculty/project/{project_id}')
        except Exception as e:
            return f"Error adding IPR: {str(e)}"
    
    publications = Publication.query.filter_by(project_id=project_id).all()
    return render_template('faculty/add_ipr.html', project=project, publications=publications)


# ==================== ADD FUNDING DETAILS ====================
@faculty_bp.route('/project/<int:project_id>/funding/add', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def add_funding(project_id):
    """Add funding details to the project"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    if request.method == 'POST':
        try:
            # Create or get funder
            funding_agency = request.form.get('funding_agency')
            funding_type = request.form.get('funding_type')
            
            funder = Funder.query.filter_by(
                funding_agency=funding_agency
            ).first()
            
            if not funder:
                funder = Funder(
                    funding_agency=funding_agency,
                    funding_type=funding_type
                )
                db.session.add(funder)
                db.session.flush()
            
            project_funding = ProjectFunding(
                project_id=project_id,
                fund_id=funder.fund_id,
                sanctioned_amount=float(request.form.get('sanctioned_amount', 0)),
                sanctioned_date=datetime.strptime(
                    request.form.get('sanctioned_date'),
                    '%Y-%m-%d'
                ) if request.form.get('sanctioned_date') else None
            )
            
            db.session.add(project_funding)
            db.session.commit()
            
            return redirect(f'/faculty/project/{project_id}')
        except Exception as e:
            return f"Error adding funding: {str(e)}"
    
    return render_template('faculty/add_funding.html', project=project)


# ==================== ADD COMPETITION ====================
@faculty_bp.route('/project/<int:project_id>/competition/add', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def add_competition(project_id):
    """Add competition participation details"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    if request.method == 'POST':
        try:
            # TODO: Implement competition model linking if needed
            # For now, store in project notes or create Competition model
            competition = Competition(
                name=request.form.get('competition_name'),
                venue=request.form.get('venue'),
                organized_by=request.form.get('organized_by')
            )
            
            db.session.add(competition)
            db.session.commit()
            
            return redirect(f'/faculty/project/{project_id}')
        except Exception as e:
            return f"Error adding competition: {str(e)}"
    
    return render_template('faculty/add_competition.html', project=project)


# ==================== CONVERT PROJECT TO STARTUP ====================
@faculty_bp.route('/project/<int:project_id>/convert-startup', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def convert_to_startup(project_id):
    """Convert a research project to a startup"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return "Unauthorized or Project not found", 404
    
    if request.method == 'POST':
        try:
            # Check if already converted
            existing_startup = Startup.query.filter_by(project_id=project_id).first()
            if existing_startup:
                return "Project already converted to startup", 400
            
            startup = Startup(
                project_id=project_id,
                startup_name=request.form.get('startup_name'),
                registration_number=request.form.get('registration_number'),
                development_status=request.form.get('development_status', 'Idea'),
                fund_amount=float(request.form.get('fund_amount', 0))
            )
            
            db.session.add(startup)
            
            # Mark project as startup converted
            project.is_startup_converted = True
            
            db.session.commit()
            
            return redirect(f'/faculty/project/{project_id}')
        except Exception as e:
            return f"Error converting to startup: {str(e)}"
    
    # Check if already a startup
    existing_startup = Startup.query.filter_by(project_id=project_id).first()
    
    return render_template('faculty/convert_startup.html', 
                         project=project, 
                         existing_startup=existing_startup)


# ==================== PROJECTS LIST ====================
@faculty_bp.route('/projects')
@login_required
@role_required('Faculty')
def projects_list():
    """View all projects for the faculty"""
    faculty_id = session['user_id']
    projects = ResearchProject.query.filter_by(faculty_id=faculty_id).all()
    
    return render_template('faculty/projects_list.html', projects=projects)


# ==================== GET AVAILABLE STUDENTS (for AJAX) ====================
@faculty_bp.route('/api/available-students/<int:project_id>')
@login_required
@role_required('Faculty')
def get_available_students(project_id):
    """Get list of students not yet in the project"""
    project = ResearchProject.query.get(project_id)
    
    if not project or project.faculty_id != session['user_id']:
        return jsonify([]), 404
    
    # Get students already in project
    used_student_ids = db.session.query(ProjectPerson.person_id).filter(
        ProjectPerson.project_id == project_id
    ).all()
    used_student_ids = [s[0] for s in used_student_ids]
    
    # Get available students
    available_students = Person.query.filter(
        Person.type == 'Student',
        ~Person.person_id.in_(used_student_ids),
        Person.is_approved == True
    ).all()
    
    return jsonify([{
        'id': s.person_id,
        'name': s.name,
        'email': s.email
    } for s in available_students])


# ==================== ANALYTICS APIs ====================
@faculty_bp.route('/api/analytics/projects')
@login_required
@role_required('Faculty')
def analytics_projects():
    """Get project status distribution for faculty"""
    faculty_id = session['user_id']
    
    projects = ResearchProject.query.filter_by(faculty_id=faculty_id).all()
    
    status_count = {
        'Proposed': 0,
        'Ongoing': 0,
        'Completed': 0,
        'On Hold': 0
    }
    
    for project in projects:
        if project.project_status in status_count:
            status_count[project.project_status] += 1
    
    return jsonify({
        'statuses': list(status_count.keys()),
        'counts': list(status_count.values())
    })


@faculty_bp.route('/api/analytics/publications')
@login_required
@role_required('Faculty')
def analytics_publications():
    """Get publication status breakdown for faculty's projects"""
    faculty_id = session['user_id']
    
    publications = db.session.query(Publication, ResearchProject).filter(
        ResearchProject.faculty_id == faculty_id,
        Publication.project_id == ResearchProject.project_id
    ).all()
    
    status_count = {
        'Submitted': 0,
        'Accepted': 0,
        'Published': 0,
        'Rejected': 0
    }
    
    for pub, _ in publications:
        if pub.status in status_count:
            status_count[pub.status] += 1
    
    return jsonify({
        'statuses': list(status_count.keys()),
        'counts': list(status_count.values())
    })


@faculty_bp.route('/api/analytics/iprs')
@login_required
@role_required('Faculty')
def analytics_iprs():
    """Get IPR grant status distribution for faculty's projects"""
    faculty_id = session['user_id']
    
    iprs = db.session.query(IPR, Publication, ResearchProject).filter(
        ResearchProject.faculty_id == faculty_id,
        Publication.project_id == ResearchProject.project_id,
        IPR.publication_id == Publication.publication_id
    ).all()
    
    status_count = {
        'Filed': 0,
        'Pending': 0,
        'Granted': 0,
        'Rejected': 0
    }
    
    for ipr, _, _ in iprs:
        if ipr.grant_status in status_count:
            status_count[ipr.grant_status] += 1
    
    return jsonify({
        'statuses': list(status_count.keys()),
        'counts': list(status_count.values())
    })


@faculty_bp.route('/api/analytics/team')
@login_required
@role_required('Faculty')
def analytics_team():
    """Get team composition for faculty's projects"""
    faculty_id = session['user_id']
    
    projects = ResearchProject.query.filter_by(faculty_id=faculty_id).all()
    project_ids = [p.project_id for p in projects]
    
    if not project_ids:
        return jsonify({
            'projects': [],
            'team_sizes': []
        })
    
    team_data = db.session.query(
        ResearchProject.project_id,
        ResearchProject.title,
        db.func.count(ProjectPerson.person_id)
    ).filter(
        ResearchProject.project_id.in_(project_ids),
        ProjectPerson.project_id == ResearchProject.project_id
    ).group_by(ResearchProject.project_id).all()
    
    project_titles = [item[1] for item in team_data]
    team_sizes = [item[2] for item in team_data]
    
    return jsonify({
        'projects': project_titles,
        'team_sizes': team_sizes
    })
