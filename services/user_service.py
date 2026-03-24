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
from repository.user_repository import UserRepository,TokenBlacklistRepository
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import jwt
from utils.errors import AppError, NotFoundError

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

class UserService:
    def __init__(self):
        self.repo = UserRepository()
        self.blacklist_repo = TokenBlacklistRepository()

    def is_valid_email(self, email: str) ->bool:
        if not email or not isinstance(email, str):
            return False
        return bool(EMAIL_REGEX.match(email))
                                                  # offset = none means "start from the beginning"
    def get_users(self, limit=None, offset=None, role=None, sort_by="id", order="asc"): # limit=None means "do not restrict the number". Datebase returns all users
        return self.repo.fetch_users(
            limit=limit,
            offset=offset,
            role=role,
            sort_by=sort_by,
            order=order)

    def get_user(self, user_id):
        user = self.repo.get_by_id(user_id)
        if not user:
            # raise LookupError("User not found")
            raise NotFoundError("User not found")
        
        return user.to_dict()

    def add_user(self, data):
        # validation: required fields
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        # validate name
        if not name or not isinstance(name, str):
            # raise ValueError("name is required and must be a non-empty string")
            raise ValueError("name is required and must be a non-empty string")

        
        # validate email presence & type
        if not email or not isinstance(email, str):
            raise ValueError("email is required and must be a non-empty string")
        
        if not password or not isinstance(password, str):
            raise ValueError("password is required and must be a non-empty string")
        
        # Validate email format
        if not self.is_valid_email(email):
            raise ValueError("email is not a valid email address")
        # Hash password
        hashed_password = generate_password_hash(password)

        # save in DB
        try:
            return self.repo.insert_user({
                "name": name.strip(), 
                "email": email.strip(),
                "password": hashed_password})
        except IntegrityError:
            # duplicate email or other DB unique constraint
            raise ValueError("email already exists")
        

    def login(self, data):
       email = data.get("email")
       password = data.get("password")

       if not email or not password:
         raise ValueError("email and password required")
      # Get user from DB
       user = self.repo.get_user_by_email(email)
       if not user:
          raise ValueError("Invalid email")
        # Check password
       if not check_password_hash(user.password, password):
          raise ValueError("Incorrect password")

       # JWT Access Token Payload

       access_payload = {
           "user_id": user.id,
           "role": user.role,
           "type": "access",
           "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
       }
       access_token = jwt.encode(access_payload, "SECRET123", algorithm="HS256")

       refresh_payload = {
           "user_id": user.id,
           "role": user.role,
            "type": "refresh",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=3)
       }

       # Create JWT token
       refresh_token = jwt.encode(refresh_payload, "SECRET123", algorithm="HS256")

       return {
           "access_token": access_token,
           "refresh_token": refresh_token
       }
    
    def refresh_access_token(self, refresh_token):
      if self.blacklist_repo.is_blacklisted(refresh_token):
          raise ValueError("Token is logged out")

      try:
          decoded = jwt.decode(refresh_token, "SECRET123", algorithms=["HS256"])

        # Must be a refresh token
          if decoded.get("type") != "refresh":
             raise ValueError("Invalid refresh token")

        # Create new access token
          new_access_payload = {
              "user_id": decoded.get("user_id"),
              # fall back to "user" if older refresh tokens lack role
              "role": decoded.get("role", "user"),
              "type": "access",
              "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }

          new_access_token = jwt.encode(new_access_payload, "SECRET123", algorithm="HS256")

          return {"access_token": new_access_token}

      except jwt.ExpiredSignatureError:
          raise ValueError("Refresh token has expired")
      except jwt.InvalidTokenError:
          raise ValueError("Invalid refresh token")
      
    def logout(self, refresh_token):
         if not refresh_token:
           raise ValueError("refresh_token required")

         self.blacklist_repo.add(refresh_token)
         return True



    def update_user(self, user_id, data):
        # basic validation: ensure at least one field is present
        if not data:
            raise ValueError("No data provided for update")

        # validate email if present
        email = data.get("email")
        if email is not None:
            if not self.is_valid_email(email):
               raise ValueError("email is not a valid email address")

        try:
            updated = self.repo.update_user(user_id, data)
        except IntegrityError:
            # convert DB unique constraint error to ValueError (duplicate email)
            raise ValueError("Email already exists")

        if not updated:
            raise LookupError("User not found")

        return updated

    def promote_to_admin(self, user_id):
       user = self.repo.get_by_id(user_id)
       if not user:
           raise LookupError("User not found")

       if user.role == "admin":
          raise ValueError("User is already admin")

       updated_user = self.repo.update_role(user_id, "admin")
       return updated_user.to_dict()


    def delete_user(self, user_id):
       deleted = self.repo.delete_user(user_id)
       if not deleted:
          raise LookupError("User not found")
       return True
