from flask import Blueprint
from ..controllers.user_controller import (
    get_all_users, 
    create_user, 
    get_user, 
    update_user, 
    delete_user,
    promote_user
)
from ..utils.auth import token_required, admin_required

user_bp = Blueprint("user_bp", __name__)

# Standard REST endpoints
user_bp.route("/", methods=["GET"])(get_all_users)
user_bp.route("/", methods=["POST"])(create_user)
user_bp.route("/<int:user_id>", methods=["GET"])(get_user)
user_bp.route("/<int:user_id>", methods=["PUT"])(update_user)
user_bp.route("/<int:user_id>", methods=["DELETE"])(delete_user)

# Special administrative actions
user_bp.route(
    "/<int:user_id>/promote",
    methods=["PUT"]
)(token_required(admin_required(promote_user)))
