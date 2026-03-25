'''
📁 services/user_service.py

Contains all business logic 
Validations + decisions 
Calls repository functions 
Returns data to controller
✔ Actual application brain 

'''


# services/user_service.py
import re
import datetime
import jwt
import logging
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from ..repository.user_repository import UserRepository, TokenBlacklistRepository
from ..utils.errors import NotFoundError, ValidationError, UnauthorizedError

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.repo = UserRepository()
        self.blacklist_repo = TokenBlacklistRepository()

    def is_valid_email(self, email: str) -> bool:
        if not email or not isinstance(email, str):
            return False
        return bool(EMAIL_REGEX.match(email))

    def get_users(self, limit=None, offset=None, role=None, sort_by="id", order="asc"):
        return self.repo.fetch_users(
            limit=limit,
            offset=offset,
            role=role,
            sort_by=sort_by,
            order=order
        )

    def get_user(self, user_id):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user.to_dict()

    def add_user(self, data):
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")

        if not name or not isinstance(name, str):
            raise ValidationError("Name is required and must be a string")
        if not email or not self.is_valid_email(email):
            raise ValidationError("A valid email is required")
        if not password or len(password) < 6:
            raise ValidationError("Password is required and must be at least 6 characters long")

        hashed_password = generate_password_hash(password)
        
        return self.repo.insert_user({
            "name": name.strip(),
            "email": email.strip().lower(),
            "password": hashed_password,
            "role": role
        })

    def login(self, data):
        email = data.get("email")
        password = data.get("password")

        user = self.repo.get_user_by_email(email.lower() if email else "")
        if not user or not check_password_hash(user.password, password):
            logger.warning(f"Failed login attempt for email: {email}")
            raise ValidationError("Invalid email or password")

        secret = current_app.config.get("SECRET_KEY")
        
        access_payload = {
            "user_id": user.id,
            "role": user.role,
            "type": "access",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        }
        access_token = jwt.encode(access_payload, secret, algorithm="HS256")

        refresh_payload = {
            "user_id": user.id,
            "role": user.role,
            "type": "refresh",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        refresh_token = jwt.encode(refresh_payload, secret, algorithm="HS256")

        logger.info(f"User logged in: {user.email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }

    def refresh_access_token(self, refresh_token):
        if self.blacklist_repo.is_blacklisted(refresh_token):
            raise UnauthorizedError("Token has been revoked")

        secret = current_app.config.get("SECRET_KEY")
        try:
            decoded = jwt.decode(refresh_token, secret, algorithms=["HS256"])
            if decoded.get("type") != "refresh":
                raise ValidationError("Invalid token type")

            new_access_payload = {
                "user_id": decoded.get("user_id"),
                "role": decoded.get("role", "user"),
                "type": "access",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
            }
            new_access_token = jwt.encode(new_access_payload, secret, algorithm="HS256")
            return {"access_token": new_access_token}

        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("Invalid refresh token")

    def logout(self, refresh_token):
        self.blacklist_repo.add(refresh_token)
        logger.info("User logged out")
        return True

    def update_user(self, user_id, data):
        if not data:
            raise ValidationError("No data provided for update")

        email = data.get("email")
        if email and not self.is_valid_email(email):
            raise ValidationError("Invalid email format")

        updated = self.repo.update_user(user_id, data)
        if not updated:
            raise NotFoundError("User not found")
        return updated

    def promote_to_admin(self, user_id):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if user.role == "admin":
            return user.to_dict()

        updated_user = self.repo.update_user(user_id, {"role": "admin"})
        return updated_user

    def delete_user(self, user_id):
        if not self.repo.delete_user(user_id):
            raise NotFoundError("User not found")
        return True
