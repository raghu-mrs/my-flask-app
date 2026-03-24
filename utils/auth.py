# utils/auth.py
from functools import wraps
from flask import request, jsonify, g
import jwt

JWT_SECRET = "SECRET123"
JWT_ALGORITHM = "HS256"

def token_required(f):
    @wraps(f)
    #wrapper() function
    def decorated(*args, **kwargs):
        # 1. Get Authorization header
        auth_header = request.headers.get("Authorization", None)

        if not auth_header:
           # auth_header = request.args.get("Authorization", None)
            return jsonify({"error": "Authorization header missing"}), 401
        
        # 2. It should start with "Bearer "
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Invalid auth header format"}), 401

        token = parts[1] # In parts one means token parts[1] = token(al6526djgsjd873ddb), parts[0] = Bearer

        # 3. Decode the token and handle errors
        try:
           # You can use decoded["user_id"] later if needed
            decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            # You can use decoded["user_id"] later if needed

            # Store user information for this request
            g.user_id = decoded.get("user_id")
            # default to "user" if not present in the token to avoid KeyError
            g.role = decoded.get("role", "user")

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        # 4. If all good, call the original function
        return f(*args, **kwargs) # Same as it is return f = get_all_users(), so return get_all_users()

    return decorated



def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, "role"):
            return jsonify({"error:" "Role not found"}),403
        
        if g.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        
        return f(*args, **kwargs)
    
    return decorated
