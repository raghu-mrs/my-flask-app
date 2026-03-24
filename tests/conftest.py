# import sys
# from pathlib import Path

import pytest

# # Ensure `my_flask_app/` is on `sys.path` so imports like `run` and `database.*`
# # work when running `pytest` from the repo root.
# APP_ROOT = Path(__file__).resolve().parents[1]
# if str(APP_ROOT) not in sys.path:
#     sys.path.insert(0, str(APP_ROOT))

from run import create_app
from database.db import db


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True


    with app.test_client() as client: #Create a fake user who can send requests to my Flask app
        with app.app_context():
            db.create_all()
        yield client
