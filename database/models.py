from .db import db
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------ PERSON (Student / Faculty / Admin) ------------------
class Person(db.Model):
    __tablename__ = 'person'

    person_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # Student / Faculty / Admin
    department = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# ------------------ RESEARCH PROJECT ------------------
class ResearchProject(db.Model):
    __tablename__ = 'research_project'

    project_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('person.person_id'))
    
    project_title = db.Column(db.String(200), nullable=False)
    project_description = db.Column(db.Text)
    domain = db.Column(db.String(100))
    department = db.Column(db.String(100))
    required_skills = db.Column(db.Text)  # Comma-separated skills
    team_size = db.Column(db.Integer)
    
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    project_status = db.Column(db.String(50), default='Proposed')  # Proposed / Ongoing / Completed / On Hold
    iic_registration_status = db.Column(db.String(50))
    project_level = db.Column(db.String(50))
    program_location = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    is_startup_converted = db.Column(db.Boolean, default=False)  # Track if converted to startup

# ------------------ PROJECT_PERSON (M:N) ------------------
class ProjectPerson(db.Model):
    __tablename__ = 'project_person'

    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.person_id'), primary_key=True)
    role = db.Column(db.String(50))  # Student / Faculty / Mentor


# ------------------ FUNDER ------------------
class Funder(db.Model):
    __tablename__ = 'funder'

    fund_id = db.Column(db.Integer, primary_key=True)
    funding_agency = db.Column(db.String(200))
    funding_type = db.Column(db.String(50))  # NGO / GOVT


# ------------------ PROJECT_FUNDING (M:N) ------------------
class ProjectFunding(db.Model):
    __tablename__ = 'project_funding'

    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'), primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('funder.fund_id'), primary_key=True)
    sanctioned_amount = db.Column(db.Float)
    sanctioned_date = db.Column(db.Date)


# ------------------ PUBLICATION ------------------
class Publication(db.Model):
    __tablename__ = 'publication'

    publication_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'))

    title = db.Column(db.String(200), nullable=False)
    publication_type = db.Column(db.String(50))  # Journal / Conference
    venue = db.Column(db.String(200))
    publication_date = db.Column(db.Date)

    indexing = db.Column(db.String(100))
    page_number = db.Column(db.String(50))
    year_of_publication = db.Column(db.Integer)
    volume = db.Column(db.String(50))

    doi = db.Column(db.String(100))
    issn_isbn = db.Column(db.String(100))
    publisher = db.Column(db.String(200))
    status = db.Column(db.String(50), default='Submitted')  # Submitted / Accepted / Published / Rejected


# ------------------ AUTHOR ------------------
class Author(db.Model):
    __tablename__ = 'author'

    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


# ------------------ PUBLICATION_AUTHOR (M:N) ------------------
class PublicationAuthor(db.Model):
    __tablename__ = 'publication_author'

    publication_id = db.Column(db.Integer, db.ForeignKey('publication.publication_id'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.author_id'), primary_key=True)
    sequence_of_author = db.Column(db.Integer)


# ------------------ IPR / PATENT ------------------
class IPR(db.Model):
    __tablename__ = 'ipr'

    ipr_id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.publication_id'))

    innovation_title = db.Column(db.String(200))
    ipr_type = db.Column(db.String(50))  # Patent / Copyright / Trademark / Design

    application_number = db.Column(db.String(100), unique=True)
    filing_date = db.Column(db.Date)
    registration_date = db.Column(db.Date)
    grant_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)

    grant_status = db.Column(db.String(50), default='Filed')  # Filed / Granted / Rejected / Pending
    ownership_type = db.Column(db.String(50))


# ------------------ STARTUP (1:1 with Project) ------------------
class Startup(db.Model):
    __tablename__ = 'startup'

    startup_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'), unique=True)

    startup_name = db.Column(db.String(200))
    registration_number = db.Column(db.String(100))
    revenue_generated = db.Column(db.Float)
    development_status = db.Column(db.String(100))
    fund_amount = db.Column(db.Float)


# ------------------ COMPETITION ------------------
class Competition(db.Model):
    __tablename__ = 'competition'

    competition_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    venue = db.Column(db.String(200))
    organized_by = db.Column(db.String(200))
    start_date_of_competition = db.Column(db.Date)
    end_date_of_competition = db.Column(db.Date)


# ------------------ PROJECT_COMPETITION (M:N) ------------------
class ProjectCompetition(db.Model):
    __tablename__ = 'project_competition'

    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'), primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.competition_id'), primary_key=True)

    team_name = db.Column(db.String(100))
    prize_money_received = db.Column(db.Float)