from flask import Flask
from database.db import db
from database import models

from database.models import Person


app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)

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

from auth.routes import auth_bp
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)