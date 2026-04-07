from flask import Flask
from database.db import db
from database import models

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)

with app.app_context():
    db.create_all()
    print("Database created successfully!")

if __name__ == "__main__":
    app.run(debug=True)