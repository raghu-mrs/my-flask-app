from app import create_app
from app.database.db import db
from app.models.user_model import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Create default admin if not exists
    if not User.query.filter_by(email="admin@example.com").first():
        admin = User(
            name="Super Admin",
            email="admin@example.com",
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@example.com / admin123")
    else:
        print("Admin user already exists.")
