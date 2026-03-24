'''
routes/users_routes.py

Groups URL endpoints with Blueprints 
Organizes routes by feature
✔ Keeps routing clean 

'''


# routes/user_routes.py
from flask import Blueprint
from controllers.user_controller import get_all_users,create_user, get_user, update_user, delete_user, login_user
from controllers.user_controller import refresh_token,logout_user
from utils.auth import token_required, admin_required

user_bp = Blueprint("user_bp", __name__)

user_bp.route("/Get_ALL_Users", methods=["GET"])(get_all_users)
user_bp.route("/Create_User", methods=["POST"])(create_user)
user_bp.route("/Get_User/<int:user_id>", methods=["GET"])(get_user)
user_bp.route("/Update_User/<int:user_id>", methods=["PUT"])(update_user)
user_bp.route("/delete_User/<int:user_id>", methods=["DELETE"])(delete_user)
user_bp.add_url_rule("/User_login/login", view_func=login_user, methods=["POST"]) # above methods are same, but just we write diff style
user_bp.add_url_rule("/refresh", view_func=refresh_token, methods=["POST"])
user_bp.add_url_rule("/logout", view_func=logout_user, methods=["POST"])

from controllers.user_controller import  promote_user
from utils.auth import token_required, admin_required

user_bp.route(
    "/<int:user_id>/promote",
    methods=["PUT"]
   )(token_required(admin_required(promote_user)))
    
    

