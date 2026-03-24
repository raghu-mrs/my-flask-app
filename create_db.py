# ---- BEGIN compatibility shim for Python 3.12+ ----
import pkgutil
if not hasattr(pkgutil, "get_loader"):
    import importlib.machinery

    def _compat_get_loader(name):
        if name == "__main__":
            return None
        spec = importlib.machinery.PathFinder.find_spec(name)
        return spec.loader if spec else None

    pkgutil.get_loader = _compat_get_loader
# ---- END compatibility shim ----


# ---- BEGIN DB creation script ----
from run import create_app
from database.db import db

# Import your models so SQLAlchemy registers them
from models.user_model import User,TokenBlacklist


app = create_app()

with app.app_context():
    db.create_all()
    print("Database created successfully!")
