"""
Application configuration and extension instances.

All Flask extensions (SQLAlchemy, Migrate, Bcrypt, Api) are created here
and initialized against a single `app` instance so they can be imported
anywhere in the project without circular-import issues.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from sqlalchemy import MetaData

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Secret key signs the session cookie. Override with an env var in production.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Session cookie settings.
# SameSite="Lax" works for local dev because the frontend (localhost:3000/4000)
# and backend (localhost:5555) share the same registrable domain ("localhost").
# In production behind different domains, set SESSION_COOKIE_SAMESITE="None"
# and SESSION_COOKIE_SECURE=True (requires HTTPS).
app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"

# Naming convention keeps auto-generated migration constraint names consistent.
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)
