'''
📁 controllers/user_controller

Entry point for HTTP requests 
Receives request → calls service layer 
Returns HTTP response
✔ Acts like MVC "controller" 

'''


# controllers/user_controller.py
from flask import request, jsonify, g
from ..services.user_service import UserService
from ..utils.auth import token_required, admin_required
from ..utils.errors import NotFoundError, ForbiddenError, ValidationError

service = UserService()

@token_required
@admin_required
def get_all_users():
    """Get all users with pagination and filtering."""
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    role = request.args.get("role")
    sort_by = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    offset = (page - 1) * limit
    users = service.get_users(limit=limit, offset=offset, role=role, sort_by=sort_by, order=order)

    return jsonify({
        "success": True,
        "message": "Users fetched successfully",
        "data": {
            "page": page,
            "limit": limit,
            "filters": {"role": role},
            "sort": {"by": sort_by, "order": order},
            "users": users
        }
    }), 200

@token_required
def get_user(user_id):
    """Get a single user by ID."""
    if not user_id:
        raise ValidationError("User ID is required")

    # Only admins or the users themselves can access their data
    if g.role != "admin" and g.user_id != user_id:
        raise ForbiddenError("Access denied: You can only access your own data")
       
    user = service.get_user(user_id)
    if not user:
        raise NotFoundError("User not found")
   
    return jsonify({
        "success": True,
        "message": "User fetched successfully",
        "data": user
    }), 200

def create_user():
    """Create a new user."""
    data = request.get_json() or {}
    new_user = service.add_user(data)
    return jsonify({
        "success": True,
        "message": "User created successfully",
        "data": new_user
    }), 201

@token_required
def update_user(user_id):
    """Update user information."""
    if g.role != "admin" and g.user_id != user_id:
        raise ForbiddenError("Access denied: You can only update your own data")

    data = request.get_json() or {}
    updated_user = service.update_user(user_id, data)
    
    return jsonify({
        "success": True,
        "message": "User updated successfully",
        "data": updated_user
    }), 200

@token_required
@admin_required
def delete_user(user_id):
    """Delete a user."""
    service.delete_user(user_id)
    return jsonify({
        "success": True,
        "message": "User deleted successfully",
        "data": None
    }), 200

def promote_user(user_id):
    """Promote a user to admin."""
    user = service.promote_to_admin(user_id)
    return jsonify({
        "success": True,
        "message": "User promoted to admin",
        "data": user
    }), 200