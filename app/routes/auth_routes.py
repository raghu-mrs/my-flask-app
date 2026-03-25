from flask import Blueprint
from ..controllers.auth_controller import login_user, refresh_token, logout_user

auth_bp = Blueprint("auth_bp", __name__)

auth_bp.route("/login", methods=["POST"])(login_user)
auth_bp.route("/refresh", methods=["POST"])(refresh_token)
auth_bp.route("/logout", methods=["POST"])(logout_user)
