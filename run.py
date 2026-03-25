# ---- BEGIN compatibility shim for Python 3.12+ ----
import pkgutil
if not hasattr(pkgutil, "get_loader"):
    import importlib.machinery

    def _compat_get_loader(name):
        # __main__ has no loader → avoid ValueError
        if name == "__main__":
            return None
        spec = importlib.machinery.PathFinder.find_spec(name)
        return spec.loader if spec else None

    pkgutil.get_loader = _compat_get_loader
# ---- END compatibility shim ----


# ---- BEGIN actual Flask app code ----
from flask import Flask, jsonify
from database.db import db
from flask_migrate import Migrate
# from flasgger import Swagger
from utils.errors import AppError

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "change_me_to_env_secret"

    db.init_app(app)


    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({
            "success":False,
            "error":{
           "message":error.message
            }
        }), error.status_code
    
    
    import logging
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logging.exception(error)
        return jsonify({
            "success": False,
            "error": {
                "message": "Internal server error"
            }
        }), 500
    
   

    # @app.errorhandler(Exception)
    # def handle_unexpected_error(error):
    #    logging.exception(error)
    #    return jsonify({
    #      "success": False,
    #      "error": {
    #         "message": "User id is required"
    #     }
    #    }),400

    migrate = Migrate(app,db)
#     swagger_template={
#       "securityDefinitions": {
#         "BearerAuth": {
#         "type": "apiKey",
#         "name": "Authorization",
#         "in": "header",
#         "description": "Enter: Bearer <JWT token>"
#        }
#       }
#    }

    # Swagger(app, template=swagger_template) # This line enables swagger

    @app.route("/")
    def home():
        return "User Management API is running"

    # Register Blueprints
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/users")

    return app


if __name__ == "__main__":
    app = create_app()
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)
