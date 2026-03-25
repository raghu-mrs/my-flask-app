import logging
from ..models.user_model import User, TokenBlacklist
from ..database.db import db
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

class UserRepository:
    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def fetch_users(self, limit=None, offset=None, role=None, sort_by="id", order="asc"):
        logger.info(f"Fetching users with limit={limit}, offset={offset}, role={role}, sort_by={sort_by}, order={order}")
        q = User.query

        if role:
            q = q.filter(User.role == role)

        # Map string sort_by to model column
        sort_columns = {
            "id": User.id,
            "name": User.name,
            "email": User.email,
            "created_at": User.created_at,
            "role": User.role
        }
        sort_col = sort_columns.get(sort_by, User.id)

        if order == "desc":
            q = q.order_by(sort_col.desc())
        else:
            q = q.order_by(sort_col.asc())

        if offset is not None:
            q = q.offset(offset)
        if limit is not None:
            q = q.limit(limit)
            
        return [u.to_dict() for u in q.all()]

    def get_by_id(self, user_id):
        return User.query.get(user_id)

    def insert_user(self, data):
        try:
            user = User(
                name=data["name"],
                email=data["email"],
                password=data["password"],
                role=data.get("role", "user")
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"User created: {user.email}")
            return user.to_dict()
        except IntegrityError:
            db.session.rollback()
            logger.warning(f"Failed to create user (duplicate email): {data.get('email')}")
            raise ValueError("User with this email already exists")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during user creation: {str(e)}")
            raise

    def update_user(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            return None

        if "name" in data:
            user.name = data["name"]
        if "email" in data:
            user.email = data["email"]
        if "role" in data:
            user.role = data["role"]

        try:
            db.session.commit()
            logger.info(f"User updated: {user_id}")
            return user.to_dict()
        except IntegrityError:
            db.session.rollback()
            logger.warning(f"Failed to update user (duplicate email): {user_id}")
            raise ValueError("Email already in use by another user")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during user update: {str(e)}")
            raise

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        try:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"User deleted: {user_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during user deletion: {str(e)}")
            raise

class TokenBlacklistRepository:
    def is_blacklisted(self, token):
        return TokenBlacklist.query.filter_by(token=token).first() is not None

    def add(self, token):
        try:
            black = TokenBlacklist(token=token)
            db.session.add(black)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during token blacklisting: {str(e)}")
            raise
