from app import create_app
from app.database.db import db
from app.models.user_model import User, TokenBlacklist

app = create_app()

with app.app_context():
    db.create_all()
    print("Database created successfully!")
