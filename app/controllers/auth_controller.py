from flask import request, jsonify
from ..services.user_service import UserService
from ..utils.errors import ValidationError, UnauthorizedError

service = UserService()

def login_user():
    """Handle user login and return tokens."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise ValidationError("Email and password are required")

    try:
        result = service.login(data)
        return jsonify({
            "success": True,
            "message": "Login successful",
            "data": result
        }), 200
    except ValueError as e:
        raise ValidationError(str(e))

def refresh_token():
    """Handle access token refresh using a refresh token."""
    data = request.get_json() or {}
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        raise ValidationError("Refresh token is required")

    try:
        new_access_token = service.refresh_access_token(refresh_token)
        return jsonify({
            "success": True,
            "message": "Access token refreshed successfully",
            "data": new_access_token
        }), 200
    except ValueError as e:
        raise UnauthorizedError(str(e))

def logout_user():
    """Handle user logout by invalidating the refresh token."""
    data = request.get_json() or {}
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        raise ValidationError("Refresh token is required for logout")

    try:
        service.logout(refresh_token)
        return jsonify({
            "success": True,
            "message": "Logged out successfully",
            "data": None
        }), 200
    except ValueError as e:
        raise ValidationError(str(e))
