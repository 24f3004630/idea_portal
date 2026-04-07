from flask import Flask
from config import Config
from database.db import db

# CREATE APP FIRST
app = Flask(__name__)
app.config.from_object(Config)

# INIT DB
db.init_app(app)

# IMPORT BLUEPRINTS AFTER APP
from auth.routes import auth_bp
from admin.routes import admin_bp
from faculty.routes import faculty_bp

# REGISTER BLUEPRINTS
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(faculty_bp)

# CREATE DB + ADMIN
from database.models import Person

with app.app_context():
    db.create_all()

    admin = Person.query.filter_by(email="admin@portal.com").first()
    if not admin:
        admin = Person(
            name="Admin",
            email="admin@portal.com",
            type="Admin",
            is_approved=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

# TEST ROUTE
@app.route('/')
def home():
    return "App Running"

if __name__ == "__main__":
    app.run(debug=True)