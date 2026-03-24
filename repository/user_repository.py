# repository/user_repository.py
from models.user_model import User
from database.db import db
from sqlalchemy.exc import IntegrityError

class UserRepository:

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()
                                                          # adding role
    def fetch_users(self, limit=None, offset=None, role=None, sort_by="id", order="asc"): 
        q = User.query

        if role:
           q = q.filter(User.role == role)

        # SORTING (safe allowlist)
        sort_columns = {
            "id": User.id,
            "name": User.name,
            "email":User.email,
            "createdd_at": User.created_at,
            "role": User.role
        }

        sort_columns = sort_columns.get(sort_by, User.id)

        if order == "desc":
           q = q.order_by(sort_columns.desc())
        else:
            q = q.order_by(sort_columns.asc())

        if offset is not None:
            q = q.offset(offset)
        if limit is not None:
            q = q.limit(limit)
        return [u.to_dict() for u in q.all()]

    def get_by_id(self, user_id):
        return User.query.get(user_id)

    def insert_user(self, data):
        user = User(
           name=data["name"],
           email=data["email"],
           password=data["password"] # New
        )
        db.session.add(user)
        db.session.commit()
        return {
            "id": user.id,
            "name":user.name,
            "email":user.email,
            "created_at":user.created_at
        }


# ... existing imports and class ...

    def update_user(self, user_id, data):
        """
        Update existing user fields (name, email). Returns updated dict or None if not found.
        """
        user = User.query.get(user_id)
        if not user:
            return None

        # update fields only if provided
        if "name" in data:
            user.name = data["name"]
        if "email" in data:
            user.email = data["email"]

        try:
            db.session.commit()
        except IntegrityError:
            # rollback and re-raise so service can handle duplicate email errors
            db.session.rollback()
            raise

        return user.to_dict()
    
    def update_role(self, user_id, new_role):
       user = User.query.get(user_id)
       if not user:
          return None

       user.role = new_role
       db.session.commit()
       return user


    
    def delete_user(self, user_id):
      """
      Delete a user by id. Returns True if deleted, False if not found.
      """
      user = User.query.get(user_id)
      if not user:
        return False

      try:
        db.session.delete(user)
        db.session.commit()
        return True
      except Exception:
        db.session.rollback()
        raise

from models.user_model import TokenBlacklist
from database.db import db

class TokenBlacklistRepository:

    def is_blacklisted(self, token):
        return TokenBlacklist.query.filter_by(token=token).first() is not None

    def add(self, token):
        black = TokenBlacklist(token=token)
        db.session.add(black)
        db.session.commit()

