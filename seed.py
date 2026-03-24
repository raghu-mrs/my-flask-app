# seed.py
from run import create_app
from database.db import db
from models.user_model import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    if not User.query.filter_by(email="mani@example.com").first():
        admin = User(
            name="Raghu(admin)", 
            email="mani@example.com",
            password =generate_password_hash("mani369"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created.")
    else:
        print("Admin already exists.")
