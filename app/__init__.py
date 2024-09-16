import importlib
from pathlib import Path

from flask import Flask

from app import init
from app.db import connection

app = Flask(__name__)

APP_DIR = Path(__file__).parent

INIT_FILE = Path("init.yml")

with app.app_context():
    for path in APP_DIR.glob("routes/*.py"):
        if path.stem == "__init__":
            continue
        module_str = path.stem
        importlib.import_module(f"app.routes.{module_str}")


connection.init()

if INIT_FILE.exists():
    init.from_file(INIT_FILE)
