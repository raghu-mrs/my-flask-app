import os
import logging
from flask import Flask, jsonify
from flask_migrate import Migrate
from .database.db import db
from .utils.errors import AppError, InternalServerError

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "prod-ready-secret-key-123")

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log")
        ]
    )
    logger = logging.getLogger(__name__)

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "success": True,
            "status": "running",
            "message": "User Management API is healthy"
        }), 200

    # Error Handlers
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            "success": False,
            "message": error.description,
            "data": None
        }), error.code

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({
            "success": False,
            "message": error.message,
            "data": None
        }), error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("An unexpected error occurred: %s", str(error))
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500

    @app.route("/")
    def home():
        return jsonify({
            "success": True,
            "message": "Welcome to User Management API",
            "version": "1.0.0"
        })

    # Register Blueprints
    from .routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/users")

    # Auth routes (login/logout can be here or in user_routes)
    from .routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
