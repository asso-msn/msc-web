"""
Should load from a file or environment variables, hardcoded for now.
"""

VARIABLE_DIR = "var"
UPLOAD_DIR = f"{VARIABLE_DIR}/uploads"
DATABASE_URI = f"sqlite:///{VARIABLE_DIR}/app.db"
