'''
📁 controllers/user_controller

Entry point for HTTP requests 
Receives request → calls service layer 
Returns HTTP response
✔ Acts like MVC "controller" 

'''


# controllers/user_controller.py
from flask import request, jsonify, g
from services.user_service import UserService
import traceback
from utils.auth import token_required, admin_required
from utils.errors import  NotFoundError, ForbiddenError, ValidationError

service = UserService()

#first execute token required(check token is valid or not)

@token_required
@admin_required
def get_all_users():
    """
    Get all users
    ---
    tags:
      - Users
    security:
      - BearerAuth: []
    responses:
      200:
        description: Success
      401:
        description: Unauthorized
    """
    
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=5, type=int)

    role = request.args.get("role")
    sort_by = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    offset = (page - 1)*limit

    users = service.get_users(limit=limit,offset=offset,role=role,sort_by=sort_by,order=order)

    return jsonify({
        "page":page,
        "limit":limit,
        "filters":{
            "role":role
        },
        "sort":{
            "by":sort_by,
            "order":order
        },
        "users":users
    }), 200

@token_required
def get_user(user_id):
        
        # user id missing
    if not user_id:
       raise ValidationError("User id is required")

    if g.role != "admin" and g.user_id != user_id:
        raise ForbiddenError("You can access only your own data")
       
    user = service.get_user(user_id)
       
    if not user:
        raise NotFoundError("User not found")
   
    return jsonify(user),200

def create_user():
    try:
        data = request.get_json() or {}
        new_user = service.add_user(data)
        return jsonify(new_user), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error":"Internal server error", "detail":str(e)}),500
    
def login_user():
    """
    User login
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      400:
        description: Invalid credentials
    """


    try:
        data = request.get_json() or {}
        result = service.login(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

def refresh_token():
    try:
        data = request.get_json() or {}
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            return jsonify({"error": "refresh_token required"}), 400

        new_access = service.refresh_access_token(refresh_token)
        return jsonify(new_access), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
       import traceback
       traceback.print_exc()   # 👈 THIS IS VERY IMPORTANT
       return jsonify({"error": str(e)}), 500


@token_required
@admin_required
def logout_user():
    try:
        data = request.get_json() or {}
        refresh_token = data.get("refresh_token")

        service.logout(refresh_token)
        return jsonify({"message": "Logged out successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400



@token_required
def update_user(user_id):
    try:
        if g.role != "admin" and g.user_id != user_id:
            return jsonify({"error": "You can update only your own data"}),403

        data = request.get_json() or {}
        updated = service.update_user(user_id, data)
        return jsonify(updated), 200
    except ValueError as e:
        # input validation or duplicate email
        return jsonify({"error": str(e)}), 400
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        # fallback for unexpected errors
        return jsonify({"error": "Internal server error"}), 500

@token_required
@admin_required
def delete_user(user_id):
    try:
        service.delete_user(user_id)
        # 204 No Content is typical for successful DELETE
        return jsonify({"message": "User deleted successfully!"}), 200
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        # debug: print full exception to server terminal so we see exact error
        import traceback
        traceback.print_exc()            # prints full traceback to terminal
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500
    


def promote_user(user_id):
    try:
        user = service.promote_to_admin(user_id)
        return jsonify({
            "message": "User promoted to admin",
            "user": user
        }), 200
    except LookupError as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400   