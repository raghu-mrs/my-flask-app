from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from .errors import UnauthorizedError, ForbiddenError

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            raise UnauthorizedError("Authorization header is missing")
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise UnauthorizedError("Invalid authorization format. Expected 'Bearer <token>'")

        token = parts[1]
        secret = current_app.config.get("SECRET_KEY")

        try:
            decoded = jwt.decode(token, secret, algorithms=["HS256"])
            g.user_id = decoded.get("user_id")
            g.role = decoded.get("role", "user")
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("Invalid token")

        return f(*args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, "role"):
            raise ForbiddenError("Role information missing from token")
        
        if g.role != "admin":
            raise ForbiddenError("Admin privileges required for this operation")
        
        return f(*args, **kwargs)
    
    return decorated
