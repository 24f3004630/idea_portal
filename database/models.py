from .db import db

# ------------------ PERSON ------------------
class Person(db.Model):
    __tablename__ = 'person'

    person_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(20))  # Student / Faculty
    department = db.Column(db.String(100))


# ------------------ PROJECT ------------------
class ResearchProject(db.Model):
    __tablename__ = 'research_project'

    project_id = db.Column(db.Integer, primary_key=True)
    project_title = db.Column(db.String(200))
    domain = db.Column(db.String(100))
    project_status = db.Column(db.String(50))


# ------------------ PROJECT_PERSON ------------------
class ProjectPerson(db.Model):
    __tablename__ = 'project_person'

    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.person_id'), primary_key=True)

    role = db.Column(db.String(50))


# ------------------ PUBLICATION ------------------
class Publication(db.Model):
    __tablename__ = 'publication'

    publication_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'))

    title = db.Column(db.String(200))
    publication_type = db.Column(db.String(50))
    doi = db.Column(db.String(100))
    status = db.Column(db.String(50))


# ------------------ IPR ------------------
class IPR(db.Model):
    __tablename__ = 'ipr'

    ipr_id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.publication_id'))

    innovation_title = db.Column(db.String(200))
    ipr_type = db.Column(db.String(50))
    application_number = db.Column(db.String(100))


# ------------------ STARTUP ------------------
class Startup(db.Model):
    __tablename__ = 'startup'

    startup_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'), unique=True)

    startup_name = db.Column(db.String(200))


# ------------------ FUNDER ------------------
class Funder(db.Model):
    __tablename__ = 'funder'

    fund_id = db.Column(db.Integer, primary_key=True)
    funding_agency = db.Column(db.String(200))


# ------------------ PROJECT_FUNDING ------------------
class ProjectFunding(db.Model):
    __tablename__ = 'project_funding'

    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'), primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('funder.fund_id'), primary_key=True)


# ------------------ COMPETITION ------------------
class Competition(db.Model):
    __tablename__ = 'competition'

    competition_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))


# ------------------ PROJECT_COMPETITION ------------------
class ProjectCompetition(db.Model):
    __tablename__ = 'project_competition'

    project_id = db.Column(db.Integer, db.ForeignKey('research_project.project_id'), primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.competition_id'), primary_key=True)