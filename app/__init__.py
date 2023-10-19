import importlib
from pathlib import Path

from flask import Flask

from app.db import connection


app = Flask(__name__)

APP_DIR = Path(__file__).parent

with app.app_context():
    for path in APP_DIR.glob("routes/*.py"):
        if path.stem == "__init__":
            continue
        module_str = path.stem
        importlib.import_module(f"app.routes.{module_str}")


connection.init()
